import asyncio
import websockets
import random


players_online = []
parties = []


def wins(party):
    str1 = party["line1"]
    str2 = party["line2"]
    str3 = party["line3"]
    if str1 == "XXX":
        return 'X'
    if str2 == "XXX":
        return 'X'
    if str3 == "XXX":
        return 'X'
    if str1[0] == "X" and str2[0] == "X" and str3[0] == "X":
        return 'X'
    if str1[1] == "X" and str2[1] == "X" and str3[1] == "X":
        return 'X'
    if str1[2] == "X" and str2[2] == "X" and str3[2] == "X":
        return 'X'
    if str1[0] == "X" and str2[1] == "X" and str3[2] == "X":
        return 'X'
    if str1[2] == "X" and str2[1] == "X" and str3[0] == "X":
        return 'O'
    if str1 == "OOO":
        return 'O'
    if str2 == "OOO":
        return 'O'
    if str3 == "OOO":
        return 'O'
    if str1[0] == "O" and str2[0] == "O" and str3[0] == "O":
        return 'O'
    if str1[1] == "O" and str2[1] == "O" and str3[1] == "O":
        return 'O'
    if str1[2] == "O" and str2[2] == "O" and str3[2] == "O":
        return 'O'
    if str1[0] == "O" and str2[1] == "O" and str3[2] == "O":
        return 'O'
    if str1[2] == "O" and str2[1] == "O" and str3[0] == "O":
        return 'O'
    return '-'


async def handler(websocket):
    await websocket.send("Добро пожаловать на игровой сервер")
    new_player = {"websocket": websocket, "in_game": False, "enemy": None, "party_id": None}
    for player in players_online:
        if not player["in_game"]:
            player["enemy"] = websocket
            player["in_game"] = True
            player["enemy_del"] = new_player
            new_player["enemy"] = player["websocket"]
            new_player["in_game"] = True
            new_player["enemy_del"] = player
            new_party = {"line1": "---",
                         "line2": "---",
                         "line3": "---",
                         "move": random.choice([player["websocket"], websocket])}
            parties.append(new_party)
            new_player["figure"] = random.choice(['X', 'O'])
            if new_player["figure"] == 'X':
                player["figure"] = 'O'
            else:
                player["figure"] = 'X'
            new_player["party_id"] = parties.index(new_party)
            player["party_id"] = parties.index(new_party)
            await player["websocket"].send("Игра началась")
            await websocket.send("Игра началась")
            if new_party["move"] == websocket:
                await websocket.send("Ваш ход")
            else:
                await player["websocket"].send("Ваш ход")
    players_online.append(new_player)
    try:
        async for message in websocket:
            if not new_player["in_game"]:
                await websocket.send("Ожидайте")
            else:
                if parties[new_player["party_id"]]["move"] == websocket:
                    vertical, horizontal = message.split(" ")
                    horizontal = int(horizontal)
                    vertical = int(vertical)
                    if horizontal < 0 or horizontal > 3 or vertical < 0 or vertical > 3:
                        await websocket.send("Ваш ход выходит за границы поля")
                    else:
                        figure = new_player["figure"]
                        str_list = list(parties[new_player["party_id"]][f"line{vertical}"])
                        if str_list[horizontal-1] != '-':
                            await websocket.send("Тут уже установлена метка")
                        else:
                            str_list[horizontal-1] = figure
                            new_str = ''.join(str_list)
                            parties[new_player["party_id"]][f"line{vertical}"] = new_str
                            res = wins(parties[new_player["party_id"]])
                            if res == '-':
                                parties[new_player["party_id"]]["move"] = new_player["enemy"]
                                await new_player["enemy"].send(parties[new_player["party_id"]]["line1"] + "\r\n" +
                                                               parties[new_player["party_id"]]["line2"] + "\r\n" +
                                                               parties[new_player["party_id"]]["line3"])
                                await new_player["enemy"].send("Ваш ход")
                                await websocket.send(parties[new_player["party_id"]]["line1"] + "\r\n" +
                                                     parties[new_player["party_id"]]["line2"] + "\r\n" +
                                                     parties[new_player["party_id"]]["line3"])
                                await websocket.send("Ход соперника")
                            elif res == figure:
                                await websocket.send(parties[new_player["party_id"]]["line1"] + "\r\n" +
                                                     parties[new_player["party_id"]]["line2"] + "\r\n" +
                                                     parties[new_player["party_id"]]["line3"])
                                await websocket.send("Вы победили")
                                await new_player['enemy'].send(parties[new_player["party_id"]]["line1"] + "\r\n" +
                                                               parties[new_player["party_id"]]["line2"] + "\r\n" +
                                                               parties[new_player["party_id"]]["line3"])
                                await new_player['enemy'].send("Вы проиграли")
                                await websocket.close()
                                await new_player['enemy'].close()
                                players_online.remove(new_player["enemy_del"])
                                players_online.remove(new_player)

                            else:
                                await websocket.send(parties[new_player["party_id"]]["line1"] + "\r\n" +
                                                     parties[new_player["party_id"]]["line2"] + "\r\n" +
                                                     parties[new_player["party_id"]]["line3"])
                                await websocket.send("Вы проиграли")
                                await new_player['enemy'].send(parties[new_player["party_id"]]["line1"] + "\r\n" +
                                                               parties[new_player["party_id"]]["line2"] + "\r\n" +
                                                               parties[new_player["party_id"]]["line3"])
                                await new_player['enemy'].send("Вы победили")
                                await websocket.close()
                                await new_player['enemy'].close()
                                players_online.remove(new_player["enemy_del"])
                                players_online.remove(new_player)

                else:
                    await websocket.send("Ожидайте хода соперника")
    except Exception as e:
        print("error")
    finally:
        if new_player in players_online:
            if new_player['party_id'] in parties:
                party = parties[new_player['party_id']]
                parties.remove(party)
            if not (new_player['enemy'] is None):
                if not new_player['enemy'].closed:
                    await new_player['enemy'].send("Соперник вышел. Вы победили")
                players_online.remove(new_player["enemy_del"])
            players_online.remove(new_player)


async def main():
    server = await websockets.serve(handler, "0.0.0.0", 8765)
    await server.wait_closed()


asyncio.run(main())

