import xapi from 'xapi';

const BASE_URL = "챗봇 서버 주소";
const INTERVAL = 1000;

let previousCount = 0;

function postToEndpoint(endpoint, data = {}) {
  const payload = {
    Url: `${BASE_URL}${endpoint}`,
    Header: ['Content-Type: application/json'],
    AllowInsecureHTTPS: true,
  };

  const body = JSON.stringify(data);

  console.log(`[전송 시도] ${endpoint}로 요청:`, body);

  xapi.command('HttpClient Post', payload, body)
    .then(() => {
      console.log(`[전송 성공] ${endpoint}`);
    })
    .catch(err => {
      console.error(`[전송 실패] ${endpoint} 오류 발생`);
      console.error('━━━━━━━━━━━━━━━━━━━━━━━');
      if (err.message) console.error('메시지:', err.message);
      if (err.code !== undefined) console.error('오류 코드:', err.code);
      if (err.stack) console.error('스택:', err.stack);
      if (err.data) {
        console.error('요청 데이터 정보:', JSON.stringify(err.data, null, 2));
      }
      console.error('━━━━━━━━━━━━━━━━━━━━━━━');
    });
}

function checkPeopleCount() {
  xapi.status.get('RoomAnalytics/PeopleCount/Current')
    .then(count => {
      const currentCount = parseInt(count);

      if (isNaN(currentCount)) {
        console.warn('[카운트 없음 또는 감지 안됨]');
        return;
      }

      console.log('[현재 감지된 인원 수]:', currentCount);

      // 상태 변화 감지
      if (previousCount <= 0 && currentCount > 0) {
        // 인원이 처음 감지됨
        postToEndpoint('/sessionStart', { count: currentCount });
      } else if (previousCount > 0 && currentCount === 0) {
        // 모든 인원이 사라짐
        postToEndpoint('/sessionReset');
      }

      previousCount = currentCount;
    })
    .catch(err => console.error('[카운트 조회 실패]', err.message));
}

// 주기적으로 감지
setInterval(checkPeopleCount, INTERVAL);