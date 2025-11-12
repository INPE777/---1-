#게임 초기화에 추가
global NOTE_SPAWN_DELAY
NOTE_SPAWN_DELAY = 3.0


# --- 노트 생성 수정
t = get_time()
if start_ticks:
    while notes and notes[0].time - NOTE_TRAVEL_TIME <= t - NOTE_SPAWN_DELAY: #조한서
        note = notes.popleft() #조한서
        note.time += NOTE_SPAWN_DELAY #조한서
        spawn_note(note)


