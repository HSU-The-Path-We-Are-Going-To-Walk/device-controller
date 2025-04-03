import xapi from "xapi";

const FASTAPI_BASE_URL = "챗봇 서버 주소";

let isCurrentlyOccupied = false;

function postSignal(endpoint) {
  const url = `${FASTAPI_BASE_URL}/${endpoint}`;
  const payload = {
    Url: url,
    Header: ["Content-Type: application/json"],
    AllowInsecureHTTPS: true,
  };

  console.log(`[${endpoint.toUpperCase()} 신호 전송] →`, url);

  xapi
    .command("HttpClient Post", payload, "")
    .then(() => {
      console.log(`[${endpoint.toUpperCase()} 전송 완료]`);
    })
    .catch((err) => {
      console.error(`[${endpoint.toUpperCase()} 전송 실패]`);
      if (err.message) console.error("메시지:", err.message);
    });
}

// 사람 수가 바뀔 때마다 호출됨
xapi.event.on("RoomAnalytics PeopleCount Current", (count) => {
  const parsed = parseInt(count);

  if (isNaN(parsed)) {
    console.warn("[감지된 인원 수가 유효하지 않음]");
    return;
  }

  console.log(`[감지된 인원 수 변경]: ${parsed}`);

  if (parsed > 0 && !isCurrentlyOccupied) {
    postSignal("sessionStart");
    isCurrentlyOccupied = true;
  } else if (parsed === 0 && isCurrentlyOccupied) {
    postSignal("sessionReset");
    isCurrentlyOccupied = false;
  }
});
