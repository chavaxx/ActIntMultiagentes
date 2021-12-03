using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;


public class Constants
{
        public const float SQUARE_LENGTH = 10f;
        public const float INITIAL_X = -65f;
        public const float INITIAL_Y = -20;

        public const float INITIAL_Z = -25f;

        public const float WAIT_TIME = 0.1f;
}

public static class JsonHelper
{
    public static T[] FromJson<T>(string json)
    {
        Wrapper<T> wrapper = JsonUtility.FromJson<Wrapper<T>>(json);
        return wrapper.Items;
    }

    public static string ToJson<T>(T[] array)
    {
        Wrapper<T> wrapper = new Wrapper<T>();
        wrapper.Items = array;
        return JsonUtility.ToJson(wrapper);
    }

    public static string ToJson<T>(T[] array, bool prettyPrint)
    {
        Wrapper<T> wrapper = new Wrapper<T>();
        wrapper.Items = array;
        return JsonUtility.ToJson(wrapper, prettyPrint);
    }

    [System.Serializable]
    private class Wrapper<T>
    {
        public T[] Items;
    }
}

[System.Serializable]
class Box
{
    public float x;
    public float y;
    public float z;

    override public string ToString()
    {
        return "X: " + x + ", Y: " + y;
    }
}

[System.Serializable]
class Agent
{
    public int state;
    public string type;
    public int x;
    public int y;
    public int z;


    override public string ToString()
    {
        return "X: " + x + ", Y: " + y;
    }
}


public class Simulation : MonoBehaviour
{
    public GameObject box;
    public GameObject robot;
    private float timer = 0.0f;
    string simulationURL = null;
    List<GameObject> agents;
    // Start is called before the first frame update
    void Start()
    {
        // myprefab = Instantiate(myprefab, new Vector3(Constants.INITIAL_X + Constants.SQUARE_LENGTH*9, Constants.INITIAL_Y, Constants.INITIAL_Z + Constants.SQUARE_LENGTH*9), Quaternion.identity);
        // Instantiate(myprefab, new Vector3(Constants.INITIAL_X, Constants.INITIAL_Y, Constants.INITIAL_Z), Quaternion.identity);
        // StartCoroutine(ConnectToMesa());
        agents = new List<GameObject>();
        StartCoroutine(ConnectToMesa());
    }

    IEnumerator ConnectToMesa()
    {
        WWWForm form = new WWWForm();

        using (UnityWebRequest www = UnityWebRequest.Post("http://localhost:5000/simulation", form))
        {
            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.Log(www.error);
            }
            else
            {
                simulationURL = www.GetResponseHeader("Location");
                string data = www.GetResponseHeader("Items"); 
                int numItems;
                int.TryParse(data, out numItems);
                Debug.Log("Connected to simulation through Web API");
                Debug.Log(numItems);
                for(int i = 0; i < numItems; i++){
                    agents.Add(Instantiate(box, new Vector3(0,0,0), Quaternion.identity));
                }
                for(int i = 0; i < 5; i++) {
                    agents.Add(Instantiate(robot, new Vector3(Constants.INITIAL_X, Constants.INITIAL_Y, Constants.INITIAL_Z), Quaternion.identity));
                }
            }
        }
    }

    IEnumerator UpdatePositions()
    {
        using (UnityWebRequest www = UnityWebRequest.Get(simulationURL))
        {
            if (simulationURL != null)
            {
                // Request and wait for the desired page.
                yield return www.SendWebRequest();

                Debug.Log(www.downloadHandler.text);
                Debug.Log("Data has been processed");
                Agent[] newAgents = JsonHelper.FromJson<Agent>(www.downloadHandler.text);

                for(int i = 0; i < newAgents.Length; i++){
                    
                    GameObject agent = agents[i];
                    Agent agentData = newAgents[i];
                    float y = Constants.INITIAL_Y;
                    float x = Constants.INITIAL_X + agentData.x * Constants.SQUARE_LENGTH;
                    float z = Constants.INITIAL_Z + agentData.y * Constants.SQUARE_LENGTH;

                    if (agentData.type == "Box") {
                        if (agentData.state == 1) {
                            y = y + 15;
                        } else if (agentData.state == 2) {
                            y = y + 10 * (agentData.z - 1);
                        }
                    }
                    agent.transform.position = new Vector3(x, y, z);
                    
                }
            }
        }
    }


    // Update is called once per frame
    void Update()
    {
        timer += Time.deltaTime;
        if (timer > Constants.WAIT_TIME)
        {
            StartCoroutine(UpdatePositions());
            timer = timer - Constants.WAIT_TIME;
        }

    }
}
