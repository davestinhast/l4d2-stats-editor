import sys, os, subprocess

if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(APP_DIR)

BRIDGE = os.path.join(APP_DIR, "sam_bridge.exe")

try:
    from rich.console import Console
    from rich.table import Table
    from rich import box
except ImportError:
    import subprocess as sp
    sp.check_call([sys.executable, "-m", "pip", "install", "rich", "--quiet"])
    from rich.console import Console
    from rich.table import Table
    from rich import box

console = Console()

# ─── Bridge ───────────────────────────────────────────────────────────────────

def check_bridge():
    if not os.path.exists(BRIDGE):
        console.print(f"[red][!] sam_bridge.exe no encontrado.[/red]")
        input("\nEnter para salir..."); sys.exit(1)

def get_stats(keys):
    try:
        r = subprocess.run([BRIDGE, "get"],
            input="\n".join(keys)+"\n", capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return {}
    for ln in r.stderr.splitlines():
        if "BRIDGE:" in ln or "FAIL:" in ln:
            console.print(f"[dim]{ln}[/dim]")
    out = {}
    for ln in r.stdout.splitlines():
        parts = ln.split("\t")
        if len(parts) >= 2:
            try: out[parts[0]] = int(parts[1])
            except ValueError: pass
    return out

def set_stats(changes):
    try:
        r = subprocess.run([BRIDGE, "set"],
            input="\n".join(f"{k}\t{v}" for k,v in changes.items())+"\n",
            capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return False
    for ln in r.stderr.splitlines():
        if "BRIDGE:" in ln or "FAIL:" in ln:
            console.print(f"[dim]{ln}[/dim]")
    return r.returncode == 0 and r.stdout.strip().startswith("OK")

# ─── Categorías con nombres REALES extraídos del schema de Steam ─────────────

CATEGORIES = {
    "1": ("General / Campaña", [
        ("Stat.GamesPlayed.Total",        "Partidas jugadas (total)"),
        ("Stat.FinaleFinished.Total",      "Finales superados"),
        ("Stat.FinaleFinished.Versus",     "Finales superados (versus)"),
        ("Stat.InfectedKilled.Total",      "Infectados eliminados (total)"),
        ("Stat.FFDamage.Total",            "Daño amistoso total"),
        ("Stat.FFDamageGameMost.Total",    "Mayor daño amistoso en una partida"),
        ("Stat.KitsUsed.Total",            "Botiquines usados"),
        ("Stat.KitsShared.Total",          "Botiquines compartidos"),
        ("Stat.PillsUsed.Total",           "Pastillas usadas"),
        ("Stat.PillsShared.Total",         "Pastillas compartidas"),
        ("Stat.AdrenalineUsed.Total",      "Adrenalina usada"),
        ("Stat.AdrenalineShared.Total",    "Adrenalina compartida"),
        ("Stat.Defibrillated.Total",       "Jugadores desfibrilados"),
        ("Stat.DefibrillatorsUsed.Total",  "Desfibriladores usados"),
        ("Stat.TeamRevived.Total",         "Compañeros revividos"),
        ("Stat.WasRevived.Total",          "Veces que te revivieron"),
        ("Stat.TeamProtected.Total",       "Veces que protegiste compañeros"),
        ("Stat.WasProtected.Total",        "Veces que te protegieron"),
        ("Stat.TotalPlayTime.Total",       "Tiempo de juego total (segundos)"),
        ("Stat.RealismGamesPlayed.Total",  "Partidas en modo realismo"),
        ("Stat.HighestSurvivorScore.Total","Mayor puntuación de equipo"),
    ]),
    "2": ("Partidas Versus", [
        ("Stat.GamesPlayed.Versus",        "Partidas versus jugadas"),
        ("Stat.GamesWon.Versus",           "Partidas versus ganadas"),
        ("Stat.GamesLost.Versus",          "Partidas versus perdidas"),
        ("Stat.PointsMost.Versus",         "Puntos máximos en versus"),
        ("Stat.SpecAttack.Boomer",         "Gordo — Ataques exitosos"),
        ("Stat.MostDamage1Life.Boomer",    "Gordo — Daño máximo en una vida"),
        ("Stat.AvgLifeSpan.Boomer",        "Gordo — Vida media (segundos)"),
        ("Stat.SpecAttack.Hunter",         "Cazador — Saltos exitosos"),
        ("Stat.MostDamage1Life.Hunter",    "Cazador — Daño máximo en una vida"),
        ("Stat.AvgLifeSpan.Hunter",        "Cazador — Vida media"),
        ("Stat.SpecAttack.Smoker",         "Fumador — Capturas exitosas"),
        ("Stat.MostDamage1Life.Smoker",    "Fumador — Daño máximo en una vida"),
        ("Stat.AvgLifeSpan.Smoker",        "Fumador — Vida media"),
        ("Stat.SpecAttack.Tank",           "Tanque — Golpes de roca"),
        ("Stat.MostDamage1Life.Tank",      "Tanque — Daño máximo en una vida"),
        ("Stat.AvgLifeSpan.Tank",          "Tanque — Vida media"),
        ("Stat.SpecAttack.Spitter",        "Escupidora — Impactos"),
        ("Stat.MostDamage1Life.Spitter",   "Escupidora — Daño máximo en una vida"),
        ("Stat.SpecAttack.Jockey",         "Jockey — Saltos exitosos"),
        ("Stat.MostDamage1Life.Jockey",    "Jockey — Daño máximo en una vida"),
        ("Stat.SpecAttack.Charger",        "Cargador — Embestidas exitosas"),
        ("Stat.MostDamage1Life.Charger",   "Cargador — Daño máximo en una vida"),
    ]),
    "3": ("Armas — Pistolas y SMG", [
        ("Stat.Pistol.Shots.Total",        "Pistola — Disparos"),
        ("Stat.Pistol.Kills.Total",        "Pistola — Bajas"),
        ("Stat.Pistol.Head.Total",         "Pistola — Headshots"),
        ("Stat.pistol_magnum.Shots.Total", "Magnum — Disparos"),
        ("Stat.pistol_magnum.Kills.Total", "Magnum — Bajas"),
        ("Stat.pistol_magnum.Head.Total",  "Magnum — Headshots"),
        ("Stat.smg.Shots.Total",           "Uzi — Disparos"),
        ("Stat.Smg.Kills.Total",           "Uzi — Bajas"),
        ("Stat.smg.Head.Total",            "Uzi — Headshots"),
        ("Stat.Smg_silenced.Shots.Total",  "SMG Silenciada — Disparos"),
        ("Stat.Smg_silenced.Kills.Total",  "SMG Silenciada — Bajas"),
        ("Stat.Smg_silenced.Head.Total",   "SMG Silenciada — Headshots"),
        ("Stat.smg_mp5.Shots.Total",       "MP5 — Disparos"),
        ("Stat.smg_mp5.Kills.Total",       "MP5 — Bajas"),
        ("Stat.smg_mp5.Head.Total",        "MP5 — Headshots"),
    ]),
    "4": ("Armas — Escopetas", [
        ("Stat.pumpshotgun.Shots.Total",   "Escopeta básica — Disparos"),
        ("Stat.pumpshotgun.Kills.Total",   "Escopeta básica — Bajas"),
        ("Stat.pumpshotgun.Head.Total",    "Escopeta básica — Headshots"),
        ("Stat.shotgun_chrome.Shots.Total","Escopeta Chrome — Disparos"),
        ("Stat.shotgun_chrome.Kills.Total","Escopeta Chrome — Bajas"),
        ("Stat.Shotgun_chrome.Head.Total", "Escopeta Chrome — Headshots"),
        ("Stat.autoshotgun.Shots.Total",   "Escopeta táctica — Disparos"),
        ("Stat.autoshotgun.Kills.Total",   "Escopeta táctica — Bajas"),
        ("Stat.AutoShotgun.Head.Total",    "Escopeta táctica — Headshots"),
        ("Stat.Shotgun_SPAS.Shots.Total",  "SPAS (escopeta combate) — Disparos"),
        ("Stat.shotgun_spas.Kills.Total",  "SPAS (escopeta combate) — Bajas"),
        ("Stat.Shotgun_SPAS.Head.Total",   "SPAS — Headshots"),
    ]),
    "5": ("Armas — Rifles y Snipers", [
        ("Stat.Rifle.Shots.Total",         "Fusil de asalto — Disparos"),
        ("Stat.Rifle.Kills.Total",         "Fusil de asalto — Bajas"),
        ("Stat.Rifle.Head.Total",          "Fusil de asalto — Headshots"),
        ("Stat.rifle_desert.Shots.Total",  "Fusil del desierto — Disparos"),
        ("Stat.Rifle_Desert.Kills.Total",  "Fusil del desierto — Bajas"),
        ("Stat.Rifle_Desert.Head.Total",   "Fusil del desierto — Headshots"),
        ("Stat.Rifle_AK47.Shots.Total",    "AK-47 — Disparos"),
        ("Stat.Rifle_AK47.Kills.Total",    "AK-47 — Bajas"),
        ("Stat.Rifle_AK47.Head.Total",     "AK-47 — Headshots"),
        ("Stat.rifle_sg552.Shots.Total",   "SG-552 — Disparos"),
        ("Stat.rifle_sg552.Kills.Total",   "SG-552 — Bajas"),
        ("Stat.rifle_sg552.Head.Total",    "SG-552 — Headshots"),
        ("Stat.hunting_rifle.Shots.Total", "Rifle de caza — Disparos"),
        ("Stat.hunting_rifle.Kills.Total", "Rifle de caza — Bajas"),
        ("Stat.hunting_rifle.Head.Total",  "Rifle de caza — Headshots"),
        ("Stat.Sniper.Shots.Total",        "Sniper militar — Disparos"),
        ("Stat.Sniper.Kills.Total",        "Sniper militar — Bajas"),
        ("Stat.Sniper.Head.Total",         "Sniper militar — Headshots"),
        ("Stat.sniper_awp.Shots.Total",    "AWP — Disparos"),
        ("Stat.sniper_awp.Kills.Total",    "AWP — Bajas"),
        ("Stat.sniper_awp.Head.Total",     "AWP — Headshots"),
        ("Stat.sniper_scout.Shots.Total",  "Scout — Disparos"),
        ("Stat.sniper_scout.Kills.Total",  "Scout — Bajas"),
        ("Stat.sniper_scout.Head.Total",   "Scout — Headshots"),
        ("Stat.grenade_launcher.Shots.Total","Lanzagranadas — Disparos"),
        ("Stat.grenade_launcher.Kills.Total","Lanzagranadas — Bajas"),
        ("Stat.rifle_m60.Shots.Total",     "M60 — Disparos"),
        ("Stat.rifle_m60.Kills.Total",     "M60 — Bajas"),
        ("Stat.machinegun.Shots.Total",    "Minigun — Disparos"),
        ("Stat.machinegun.Kills.Total",    "Minigun — Bajas"),
    ]),
    "6": ("Armas — Cuerpo a cuerpo", [
        ("Stat.baseball_bat.Kills.Total",  "Bate de béisbol — Bajas"),
        ("Stat.chainsaw.Kills.Total",      "Motosierra — Bajas"),
        ("Stat.cricket_bat.Kills.Total",   "Bate de críquet — Bajas"),
        ("Stat.crowbar.Kills.Total",       "Palanca — Bajas"),
        ("Stat.electric_guitar.Kills.Total","Guitarra eléctrica — Bajas"),
        ("Stat.fireaxe.Kills.Total",       "Hacha de bombero — Bajas"),
        ("Stat.frying_pan.Kills.Total",    "Sartén — Bajas"),
        ("Stat.katana.Kills.Total",        "Katana — Bajas"),
        ("Stat.machete.Kills.Total",       "Machete — Bajas"),
        ("Stat.tonfa.Kills.Total",         "Tonfa — Bajas"),
        ("Stat.golfclub.Kills.Total",      "Palo de golf — Bajas"),
        ("Stat.pitchfork.Kills.Total",     "Horca — Bajas"),
        ("Stat.shovel.Kills.Total",        "Pala — Bajas"),
        ("Stat.knife.Kills.Total",         "Cuchillo — Bajas"),
    ]),
    "7": ("Modo Supervivencia y Recolecta", [
        ("Stat.SurvivalGamesPlayed.Total", "Supervivencia — Partidas jugadas"),
        ("Stat.ScavengeGamesPlayed.Total", "Recolecta — Partidas jugadas"),
        ("Stat.GamesPlayed.Total",         "Total partidas todas modalidades"),
    ]),
}

# ─── Cache y UI ───────────────────────────────────────────────────────────────

_cache = {}

def fetch_category(stats_list):
    keys = [k for k, _ in stats_list]
    missing = [k for k in keys if k not in _cache]
    if missing:
        console.print(f"[dim]Cargando {len(missing)} stats de Steam...[/dim]")
        _cache.update(get_stats(missing))
    return {k: _cache.get(k, 0) for k in keys}

def show_table(stats_list, values, title):
    t = Table(title=title, box=box.SIMPLE_HEAVY,
              title_style="bold white", header_style="bold cyan", show_lines=False)
    t.add_column("#",      style="dim",    width=4,  justify="right")
    t.add_column("Stat",   style="white",  min_width=40)
    t.add_column("Actual", style="yellow", width=14, justify="right")
    for i, (key, name) in enumerate(stats_list, 1):
        t.add_row(str(i), name, f"{values.get(key, 0):,}")
    console.print(t)

def edit_category(stats_list, values, pending):
    console.print("[dim]Número nuevo + Enter para cambiar. Solo Enter = skip.[/dim]\n")
    for key, name in stats_list:
        current = values.get(key, 0)
        raw = input(f"  {name:<42} (actual: {current:>10,})  → ").strip()
        if not raw: continue
        try:
            pending[key] = int(raw)
            console.print(f"    [green]✎ en cola[/green]")
        except ValueError:
            console.print(f"    [red]número inválido, skip[/red]")
    return pending

def print_menu(n):
    console.print("\n[bold cyan]═══ Editor de Stats L4D2 ═══[/bold cyan]")
    for k, (title, _) in CATEGORIES.items():
        console.print(f"  [cyan][{k}][/cyan]  {title}")
    console.print(f"  [cyan][V][/cyan]  Ver categoría (sin editar)")
    console.print(f"  [cyan][A][/cyan]  [bold green]Aplicar cambios a Steam  ({n} en cola)[/bold green]")
    console.print(f"  [cyan][Q][/cyan]  Salir sin guardar\n")

def main():
    os.system("title Editor de Stats L4D2")
    os.system("cls")
    console.print("[bold white]\n  Editor de Stats — Left 4 Dead 2\n  Steam abierto  |  L4D2 cerrado\n[/bold white]")
    check_bridge()
    pending = {}

    while True:
        print_menu(len(pending))
        choice = input("  Opción: ").strip().upper()

        if choice in CATEGORIES:
            title, stats_list = CATEGORIES[choice]
            os.system("cls")
            console.print(f"\n[bold white]── {title} ──[/bold white]")
            values = fetch_category(stats_list)
            for k, v in pending.items():
                if k in values: values[k] = v
            show_table(stats_list, values, title)
            console.print()
            if input("  ¿Editar esta categoría? (s/n): ").strip().lower() == "s":
                pending = edit_category(stats_list, values, pending)
            os.system("cls")

        elif choice == "V":
            console.print("\n  ¿Qué categoría?: ", end="")
            sub = input().strip()
            if sub in CATEGORIES:
                title, stats_list = CATEGORIES[sub]
                os.system("cls")
                show_table(stats_list, fetch_category(stats_list), title)
                input("\n  Enter para volver..."); os.system("cls")

        elif choice == "A":
            if not pending:
                console.print("[yellow]  Nada en cola.[/yellow]"); continue
            os.system("cls")
            name_map = {k: n for _, sl in CATEGORIES.values() for k, n in sl}
            preview = Table(title=f"Vista previa — {len(pending)} cambios",
                            box=box.SIMPLE_HEAVY, header_style="bold cyan")
            preview.add_column("Stat",        style="white",  min_width=40)
            preview.add_column("Valor nuevo", style="green",  justify="right")
            for k, v in pending.items():
                preview.add_row(name_map.get(k, k), f"{v:,}")
            console.print(preview)
            if input("\n  ¿Aplicar a Steam? (s/n): ").strip().lower() == "s":
                if set_stats(pending):
                    console.print(f"[green]✓  {len(pending)} stats guardados![/green]")
                    for k in pending: _cache.pop(k, None)
                    pending.clear()
                else:
                    console.print(f"[red]Falló.[/red]")
            else:
                console.print("[dim]Cancelado.[/dim]")

        elif choice == "Q":
            if pending:
                if input(f"  {len(pending)} cambios sin guardar. ¿Salir? (s/n): ").strip().lower() != "s":
                    continue
            break
        else:
            console.print("[red]  Opción no válida.[/red]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[dim]Saliendo.[/dim]"); sys.exit(0)
