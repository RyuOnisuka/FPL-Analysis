#!/usr/bin/env python3
"""
FPL Data Updater Script
Run this script anytime to refresh your FPL squad data, live scores, fixtures, and player statistics.
Usage: python3 update_data.py [TEAM_ID]
"""

import urllib.request
import json
import ssl
import sys
import os

DEFAULT_TEAM_ID = 4554263

def update_fpl_data(team_id=DEFAULT_TEAM_ID):
    print(f"🔄 Updating FPL data for Team ID: {team_id}...")
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    def get_json(url):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            return json.loads(resp.read().decode('utf-8'))

    try:
        print("  - Fetching bootstrap static (players, teams, gameweeks)...")
        bootstrap = get_json('https://fantasy.premierleague.com/api/bootstrap-static/')
        
        print("  - Fetching fixtures...")
        fixtures = get_json('https://fantasy.premierleague.com/api/fixtures/')
        
        print(f"  - Fetching team entry summary ({team_id})...")
        entry = get_json(f'https://fantasy.premierleague.com/api/entry/{team_id}/')
        
        print(f"  - Fetching team history ({team_id})...")
        history = get_json(f'https://fantasy.premierleague.com/api/entry/{team_id}/history/')

        events = bootstrap.get('events', [])
        current_gw = next((e for e in events if e.get('is_current')), None) or events[0]
        cur_gw_id = current_gw['id']
        print(f"  - Current Gameweek: {cur_gw_id}")

        print(f"  - Fetching squad picks for GW{cur_gw_id}...")
        picks = get_json(f'https://fantasy.premierleague.com/api/entry/{team_id}/event/{cur_gw_id}/picks/')
        
        print(f"  - Fetching live match stats for GW{cur_gw_id}...")
        live = get_json(f'https://fantasy.premierleague.com/api/event/{cur_gw_id}/live/')

        league_standings = {}
        classic_leagues = entry.get('leagues', {}).get('classic', [])
        print(f"  - Fetching standings for {len(classic_leagues)} leagues...")
        for l in classic_leagues:
            lid = l['id']
            try:
                std = get_json(f'https://fantasy.premierleague.com/api/leagues-classic/{lid}/standings/')
                league_standings[lid] = std
            except Exception as e:
                print(f"    ⚠️ Could not fetch standings for league {lid}: {e}")

        payload = {
            'team_id': team_id,
            'entry': entry,
            'history': history,
            'current_gw': cur_gw_id,
            'picks': picks,
            'live': live,
            'league_standings': league_standings,
            'bootstrap': {
                'events': bootstrap['events'],
                'teams': bootstrap['teams'],
                'element_types': bootstrap['element_types'],
                'elements': bootstrap['elements']
            },
            'fixtures': fixtures
        }

        output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fpl_data.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        output_js = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fpl_data.js')
        with open(output_js, 'w', encoding='utf-8') as f:
            f.write("window.INITIAL_FPL_DATA = " + json.dumps(payload, ensure_ascii=False) + ";\n")

        print(f"✅ Successfully updated {output_file} & {output_js}")
        print(f"🎉 Team: {entry.get('name')} | Manager: {entry.get('player_first_name')} {entry.get('player_last_name')}")
        print(f"🏆 Overall Points: {entry.get('summary_overall_points')} | GW Points: {entry.get('summary_event_points')}")
        return True
    except Exception as e:
        print(f"❌ Error updating data: {e}")
        return False

if __name__ == '__main__':
    t_id = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TEAM_ID
    update_fpl_data(t_id)
