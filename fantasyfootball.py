def app():
    from espn_api.football import League
    import pandas as pd
    import streamlit as st

    st.header('Fantasy Football Records by Schedule')
    # Pennoni Younglings
    league = League(league_id=310334683, year=2022, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

    # Family League
    # league = League(league_id=1725372613, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

    # EBC League
    # league = League(league_id=1118513122, year=2022, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

    scoresList = []
    schedList = []
    count = 0
    keyList = []
    for team in league.teams:
        scoresList.append(team.scores)
        schedList.append(team.schedule)
        keyList.append([count, team.team_name])
        count += 1
    
    # print(schedList[5][0])
    # print(scoresList[5][0])
    # print(scoresList[5])
    # print(league.scoreboard(week=1))

    # scoreboard1 = league.scoreboard(week=1)
    # print(scoreboard1[4])
    # print(scoreboard1[4].home_score)
    # print(scoreboard1[4].home_team)
    # print(scoreboard1[4].away_score)

    # teamToUse = "The Golden Receivers"
    # teamToUse = "PAI Athletic Director"
    # teamToUse = "Girth Brooks"

    # teamToUse = "Golden Receivers"
    # teamToUse = "Team Janstrong"
    # teamToUse = "Lockett inma pockett"
    # teamToUse = "DadBod 69ers"
    # teamToUse = "Kuppcakes  ."

    # teamToUse = "The Hungry Dogs"
    # teamToUse = "Abyss Diamond Eyes"
    names = []
    for k in keyList:
        names.append(k[1])

    tot = 1
    win = 0
    loss = 0
    tie = 0
    records = []
    names.insert(0, "Teams")
    # df = pd.DataFrame(columns=namesIndex)
    masterList = []
    for i in range(len(keyList)):
        for team in keyList:
            checkTeam = team[1]
            while tot < 5:
                scoreboard = league.scoreboard(week=tot)
                myTeam = keyList[i][1]
                for sc in scoreboard:
                    myScore = scoresList[i][tot-1]
                    if sc.home_team.team_name == checkTeam:
                        if myScore > sc.away_score:
                            win += 1
                        elif myScore < sc.away_score:
                            loss += 1
                        else:
                            if myTeam == sc.away_team.team_name:
                                if myScore > sc.home_score:
                                    win += 1
                                elif myScore < sc.home_score:
                                    loss += 1
                            else:
                                tie += 1
                    elif sc.away_team.team_name == checkTeam:
                        if myScore > sc.home_score:
                            win += 1
                        elif myScore < sc.home_score:
                            loss += 1
                        else:
                            if myTeam == sc.home_team.team_name:
                                if myScore > sc.away_score:
                                    win += 1
                                elif myScore < sc.away_score:
                                    loss += 1
                            else:
                                tie += 1
                tot += 1
            record = str(win) + " - " + str(loss) + " - " + str(tie)
            records.append(record)
            tot = 1
            win = 0
            loss = 0
            tie = 0
        records.insert(0, myTeam)
        masterList.append(records)
        records = []
        
    df = pd.DataFrame(masterList, columns = names)
    df = df.set_index("Teams")
    st.dataframe(df, height=500)
    # print(df)
    # print(tabulate(records, headers=[
    #       "Team",
    #       "Record",]))
        
    # scList = []
    # for mu in scoreboard1:
    #     ht = mu.home_team.team_name
    #     hs = mu.home_score
    #     at = mu.away_team.team_name
    #     asc = mu.away_score
    #     scList.append([(ht,hs),(at,asc)])
    # print(scList)
    # teamList = []
    # for team in league.teams:
    #     teamList.append(team.team_name)
    # print(teamList)