using UnityEngine;

public class SoundManagerUI : MonoBehaviour
{
    [Header("UI Sound Effects")]
    public AudioClip buttonEnterPanelSound;
    public AudioClip buttonExitPanelSound;
    public AudioClip pauseMenuOpenSound;
    public AudioClip buttonClickSound;
    
    [Header("Audio Samples")]
    public AudioClip voiceSampleClip;
    public AudioClip sfxSampleClip;
    public AudioClip musicSampleClip;
    
    [Header("Audio Sources")]
    public AudioSource uiAudioSource;
    public AudioSource voiceAudioSource;
    public AudioSource sfxAudioSource;
    public AudioSource musicAudioSource;
    
    public static SoundManagerUI Instance;
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    public void PlayButtonEnterPanel()
    {
        if (buttonEnterPanelSound != null && uiAudioSource != null)
            uiAudioSource.PlayOneShot(buttonEnterPanelSound);
    }
    
    public void PlayButtonExitPanel()
    {
        if (buttonExitPanelSound != null && uiAudioSource != null)
            uiAudioSource.PlayOneShot(buttonExitPanelSound);
    }
    
    public void PlayPauseMenuOpen()
    {
        if (pauseMenuOpenSound != null && uiAudioSource != null)
            uiAudioSource.PlayOneShot(pauseMenuOpenSound);
    }
    
    public void PlayButtonClick()
    {
        if (buttonClickSound != null && uiAudioSource != null)
            uiAudioSource.PlayOneShot(buttonClickSound);
    }
    
    public void PlayVoiceSample(float volume)
    {
        StopAllSamples();
        if (voiceSampleClip != null && voiceAudioSource != null)
        {
            voiceAudioSource.volume = volume;
            voiceAudioSource.clip = voiceSampleClip;
            voiceAudioSource.loop = true;
            voiceAudioSource.Play();
        }
    }
    
    public void PlaySFXSample(float volume)
    {
        StopAllSamples();
        if (sfxSampleClip != null && sfxAudioSource != null)
        {
            sfxAudioSource.volume = volume;
            sfxAudioSource.clip = sfxSampleClip;
            sfxAudioSource.loop = true;
            sfxAudioSource.Play();
        }
    }
    
    public void PlayMusicSample(float volume)
    {
        StopAllSamples();
        if (musicSampleClip != null && musicAudioSource != null)
        {
            musicAudioSource.volume = volume;
            musicAudioSource.clip = musicSampleClip;
            musicAudioSource.loop = true;
            musicAudioSource.Play();
        }
    }
    
    public void StopAllSamples()
    {
        if (voiceAudioSource != null) voiceAudioSource.Stop();
        if (sfxAudioSource != null) sfxAudioSource.Stop();
        if (musicAudioSource != null) musicAudioSource.Stop();
    }
}