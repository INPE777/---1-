
center_fill_img = load_scaled("img/center_fill.png", (150, 150))#조한서 #img폴더의 center_fill.png load_scaled하기 임시로 이미지 넣어둠
max_score = 4650 #조한서 #최고 점수(목표점수) 이 점수 다 채워지면 이미지 완성

if center_fill_img: #조한서
    orig_w, orig_h = center_fill_img.get_size() #조한서
    fill_h = max(0, min(orig_h, int((score / max_score) * orig_h))) #조한서 #채워지는 높이의 최대, 최소 설정)

    if fill_h > 0: #조한서
        src = pygame.Rect(0, orig_h - fill_h, orig_w, fill_h) #조한서 #원본 이미지에서 잘라낼 영역 설정 아래쪽 부터 fill_h까지
        chunk = center_fill_img.subsurface(src).copy() #조한서 #잘라낸 부분을 chunk로 저장
        dest = chunk.get_rect(midbottom=(CENTER[0], CENTER[1] + 75)) #조한서 #청크 출력 위치 설정
        screen.blit(chunk, dest.topleft) #조한서
else: #조한서
    pygame.draw.circle(screen, WHITE, CENTER, TARGET_RADIUS, 5) #조한서