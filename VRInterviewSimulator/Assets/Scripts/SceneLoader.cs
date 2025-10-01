using UnityEngine;
using UnityEngine.SceneManagement;

public class SceneLoader : MonoBehaviour
{
    public static void LoadSceneWithLoading(string sceneName)
    {
        PlayerPrefs.SetString("TargetScene", sceneName);
        SceneManager.LoadScene("LoadingScene");
    }
    
    public void LoadScene(string sceneName)
    {
        LoadSceneWithLoading(sceneName);
    }
}