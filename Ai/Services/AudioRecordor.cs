using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using NAudio.Wave;

public class AudioRecorder
{
    private WaveInEvent? _waveIn;
    private WaveFileWriter? _writer;
    private TaskCompletionSource<bool>? _stoppedTcs;

    /// <summary>
    /// Start mic capture, wait at least <paramref name="minMs"/>, then
    /// stop when ENTER is received on stdin (from Unity's RedirectStandardInput),
    /// or when <paramref name="maxMs"/> total time elapses if no ENTER arrives.
    /// Ensures the WAV is finalized before returning.
    /// Throws if too little audio was captured.
    /// </summary>
    public async Task RecordUntilEnterAsync(string outputFile, int minMs = 1500, int maxMs = 15000)
    {
        if (minMs <= 0) minMs = 1;
        if (maxMs < minMs) maxMs = minMs;

        // Ensure target directory exists
        var fullPath = Path.GetFullPath(outputFile);
        var dir = Path.GetDirectoryName(fullPath);
        if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);

        _waveIn = new WaveInEvent { WaveFormat = new WaveFormat(16000, 1) };
        _writer = new WaveFileWriter(fullPath, _waveIn.WaveFormat);
        _stoppedTcs = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);

        long totalBytes = 0;

        _waveIn.DataAvailable += (_, a) =>
        {
            // Guard in case stop/dispose raced
            var w = _writer;
            if (w != null && a.BytesRecorded > 0)
            {
                w.Write(a.Buffer, 0, a.BytesRecorded);
                totalBytes += a.BytesRecorded;
            }
        };

        _waveIn.RecordingStopped += (_, __) =>
        {
            try { _writer?.Dispose(); } catch { /* ignore */ }
            _writer = null;
            try { _waveIn?.Dispose(); } catch { /* ignore */ }
            _waveIn = null;
            _stoppedTcs?.TrySetResult(true);
        };

        _waveIn.StartRecording();
        Console.WriteLine($"Recording... (min {minMs}ms)");

        // Wait for ENTER on a background task (null if stdin closed)
        var enterTask = Task.Run(async () =>
        {
            try
            {
                var line = await Console.In.ReadLineAsync().ConfigureAwait(false);
                return line != null; // true if got ENTER
            }
            catch
            {
                return false;        // stdin unavailable
            }
        });

        // Always capture at least minMs
        await Task.Delay(minMs).ConfigureAwait(false);

        // After minMs, wait either for ENTER or for the remaining timeout
        var remaining = Math.Max(1, maxMs - minMs);
        using var cts = new CancellationTokenSource();
        var timeoutTask = Task.Delay(remaining, cts.Token);

        await Task.WhenAny(enterTask, timeoutTask).ConfigureAwait(false);
        cts.Cancel();

        // Stop and wait for WAV finalization
        _waveIn.StopRecording();
        if (_stoppedTcs != null)
            await _stoppedTcs.Task.ConfigureAwait(false);

        // Sanity check: ~0.25s (16kHz mono 16-bit ≈ 32kB/s)
        if (totalBytes < 8000)
            throw new InvalidOperationException("Audio too short. Please speak for at least a second.");

        Console.WriteLine($"Stopped. Wrote {totalBytes} bytes to {fullPath}");
    }

    /// <summary>
    /// Backward-compatible wrapper if existing code calls Record(...).
    /// Uses the same defaults as RecordUntilEnterAsync.
    /// </summary>
    public Task Record(string outputFile) => RecordUntilEnterAsync(outputFile, 1500, 15000);
}
