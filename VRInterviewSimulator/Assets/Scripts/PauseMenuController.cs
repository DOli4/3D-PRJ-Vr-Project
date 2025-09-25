using UnityEngine;
using UnityEngine.SceneManagement;

public class PauseMenuController : MonoBehaviour
{
    [SerializeField] private GameObject pauseMenuPanel;
    [SerializeField] private GameObject settingsPanel;
    
    private bool isPaused = false;

    public void ResumeGame()
    {
        isPaused = false;
        Time.timeScale = 1f;
        pauseMenuPanel.SetActive(false);
    }

    public void PauseGame()
    {
        isPaused = true;
        Time.timeScale = 0f;
        if (SoundManagerUI.Instance != null)
            SoundManagerUI.Instance.PlayPauseMenuOpen();
        pauseMenuPanel.SetActive(true);
    }

    public void OpenSettings()
    {
        if (SoundManagerUI.Instance != null)
            SoundManagerUI.Instance.PlayButtonEnterPanel();
        pauseMenuPanel.SetActive(false);
        settingsPanel.SetActive(true);
    }

    public void QuitToMainMenu()
    {
        Time.timeScale = 1f;
        SceneManager.LoadScene("SampleScene");
    }

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.Escape))
        {
            if (settingsPanel.activeInHierarchy)
            {
                // If settings is open, go back to pause menu
                if (settingsPanel.GetComponent<SettingsMenuController>() != null)
                    settingsPanel.GetComponent<SettingsMenuController>().BackToMenu();
            }
            else if (isPaused)
            {
                ResumeGame();
            }
            else
            {
                PauseGame();
            }
        }
    }
}