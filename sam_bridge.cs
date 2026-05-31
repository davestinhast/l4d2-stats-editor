using System;
using System.IO;
using System.Threading;
using SAM.API;
using SAM.API.Callbacks;

class SamBridge
{
    static void Main(string[] args)
    {
        string mode = args.Length > 0 ? args[0] : "get";

        string dir = Path.GetDirectoryName(
            System.Reflection.Assembly.GetExecutingAssembly().Location);
        foreach (string d in new[] { dir, Directory.GetCurrentDirectory() })
            try { File.WriteAllText(Path.Combine(d, "steam_appid.txt"), "550"); } catch { }

        var client = new Client();
        try { client.Initialize(550); }
        catch (Exception ex)
        {
            Console.Error.WriteLine("FAIL:Init:" + ex.Message);
            Environment.Exit(1);
        }

        ulong steamId = client.SteamUser.GetSteamId();
        Console.Error.WriteLine("BRIDGE:SteamID=" + steamId);

        bool received = false;
        var cb = client.CreateAndRegisterCallback<UserStatsReceived>();
        cb.OnRun += (data) => { received = true; };

        client.SteamUserStats.RequestUserStats(steamId);

        var deadline = DateTime.Now.AddSeconds(15);
        while (!received && DateTime.Now < deadline)
        {
            client.RunCallbacks(false);
            Thread.Sleep(50);
        }

        Console.Error.WriteLine(received ? "BRIDGE:stats OK" : "BRIDGE:WARN timeout");

        if (mode == "get")
        {
            string line;
            while ((line = Console.ReadLine()) != null)
            {
                line = line.Trim();
                if (line.Length == 0) continue;
                int val = 0;
                bool found = client.SteamUserStats.GetStatValue(line, out val);
                Console.WriteLine(line + "\t" + val + "\t" + (found ? "1" : "0"));
            }
        }
        else if (mode == "set")
        {
            int changed = 0;
            string line;
            while ((line = Console.ReadLine()) != null)
            {
                var parts = line.Split('\t');
                if (parts.Length >= 2)
                {
                    int val;
                    if (int.TryParse(parts[1].Trim(), out val))
                    {
                        client.SteamUserStats.SetStatValue(parts[0].Trim(), val);
                        changed++;
                    }
                }
            }
            bool ok = client.SteamUserStats.StoreStats();
            Console.WriteLine(ok ? "OK:" + changed : "FAIL:StoreStats");
        }

        client.Dispose();
    }
}
