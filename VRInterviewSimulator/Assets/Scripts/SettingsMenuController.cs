using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Audio;
using TMPro;

public class SettingsMenuController : MonoBehaviour
{
    [Header("Audio Controls")]
    public Slider masterVolumeSlider;
    public Slider sfxVolumeSlider;
    public Slider voiceVolumeSlider;
    public Slider musicVolumeSlider;
    public AudioMixer audioMixer;

    [Header("Accessibility")]
    public Toggle subtitlesToggle;
    public Toggle colorblindToggle;

    [Header("Microphone")]
    public TMP_Dropdown microphoneDropdown;

    [Header("UI Panels")]
    public GameObject settingsPanel;
    public GameObject pauseMenuPanel;

    void Start()
    {
        LoadSettings();
        PopulateMicrophoneDropdown();
        SetupSliderListeners();
    }

    void SetupSliderListeners()
    {
        masterVolumeSlider.onValueChanged.AddListener(SetMasterVolume);
        sfxVolumeSlider.onValueChanged.AddListener(SetSFXVolume);
        sfxVolumeSlider.onValueChanged.AddListener(PlaySFXSample);
        voiceVolumeSlider.onValueChanged.AddListener(SetVoiceVolume);
        voiceVolumeSlider.onValueChanged.AddListener(PlayVoiceSample);
        musicVolumeSlider.onValueChanged.AddListener(SetMusicVolume);
        musicVolumeSlider.onValueChanged.AddListener(PlayMusicSample);
    }

    public void SetMasterVolume(float volume)
    {
        audioMixer.SetFloat("MasterVolume", volume <= 0.001f ? -80f : Mathf.Log10(volume) * 20);
    }

    public void SetSFXVolume(float volume)
    {
        audioMixer.SetFloat("SFXVolume", volume <= 0.001f ? -80f : Mathf.Log10(volume) * 20);
    }

    public void SetVoiceVolume(float volume)
    {
        audioMixer.SetFloat("VoiceVolume", volume <= 0.001f ? -80f : Mathf.Log10(volume) * 20);
    }

    public void SetMusicVolume(float volume)
    {
        audioMixer.SetFloat("MusicVolume", volume <= 0.001f ? -80f : Mathf.Log10(volume) * 20);
    }



    void PopulateMicrophoneDropdown()
    {
        microphoneDropdown.ClearOptions();
        foreach (string device in Microphone.devices)
        {
            microphoneDropdown.options.Add(new TMP_Dropdown.OptionData(device));
        }
        microphoneDropdown.RefreshShownValue();
    }



    public void ResetToDefaults()
    {
        masterVolumeSlider.value = 0.8f;
        sfxVolumeSlider.value = 0.7f;
        voiceVolumeSlider.value = 0.8f;
        musicVolumeSlider.value = 0.5f;
        subtitlesToggle.isOn = false;
        colorblindToggle.isOn = false;
        microphoneDropdown.value = 0;
    }

    public void PlayVoiceSample(float volume)
    {
        if (SoundManagerUI.Instance != null)
            SoundManagerUI.Instance.PlayVoiceSample(volume);
    }
    
    public void PlaySFXSample(float volume)
    {
        if (SoundManagerUI.Instance != null)
            SoundManagerUI.Instance.PlaySFXSample(volume);
    }
    
    public void PlayMusicSample(float volume)
    {
        if (SoundManagerUI.Instance != null)
            SoundManagerUI.Instance.PlayMusicSample(volume);
    }
    
    void OnDisable()
    {
        if (SoundManagerUI.Instance != null)
            SoundManagerUI.Instance.StopAllSamples();
    }

    public void ApplySettings()
    {
        if (SoundManagerUI.Instance != null)
            SoundManagerUI.Instance.PlayButtonExitPanel();
        SaveSettings();
        BackToMenu();
    }

    public void CancelSettings()
    {
        if (SoundManagerUI.Instance != null)
            SoundManagerUI.Instance.PlayButtonExitPanel();
        LoadSettings();
        BackToMenu();
    }

    public void BackToMenu()
    {
        if (SoundManagerUI.Instance != null)
            SoundManagerUI.Instance.PlayButtonExitPanel();
        settingsPanel.SetActive(false);
        pauseMenuPanel.SetActive(true);
    }

    void SaveSettings()
    {
        PlayerPrefs.SetFloat("MasterVolume", masterVolumeSlider.value);
        PlayerPrefs.SetFloat("SFXVolume", sfxVolumeSlider.value);
        PlayerPrefs.SetFloat("VoiceVolume", voiceVolumeSlider.value);
        PlayerPrefs.SetFloat("MusicVolume", musicVolumeSlider.value);
        PlayerPrefs.SetInt("Subtitles", subtitlesToggle.isOn ? 1 : 0);
        PlayerPrefs.SetInt("Colorblind", colorblindToggle.isOn ? 1 : 0);
        PlayerPrefs.SetInt("Microphone", microphoneDropdown.value);
        PlayerPrefs.Save();
    }

    void LoadSettings()
    {
        masterVolumeSlider.value = PlayerPrefs.GetFloat("MasterVolume", 0.8f);
        sfxVolumeSlider.value = PlayerPrefs.GetFloat("SFXVolume", 0.7f);
        voiceVolumeSlider.value = PlayerPrefs.GetFloat("VoiceVolume", 0.8f);
        musicVolumeSlider.value = PlayerPrefs.GetFloat("MusicVolume", 0.5f);
        subtitlesToggle.isOn = PlayerPrefs.GetInt("Subtitles", 0) == 1;
        colorblindToggle.isOn = PlayerPrefs.GetInt("Colorblind", 0) == 1;
        microphoneDropdown.value = PlayerPrefs.GetInt("Microphone", 0);
    }
}