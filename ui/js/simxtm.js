/**
 * @fileoverview Test Process Manager
 * @author croft@famros.co.kr
 * @version 1.0.0
 * @since 2024.01.18
 */

// KS X 3267 센서 리스트
const devnames = {
  0: "장비없음",
  1: "온도",
  2: "습도",
  3: "이슬점",
  4: "감우",
  5: "유량",
  6: "강우",
  7: "일사",
  8: "풍속",
  9: "풍향", 
  10: "전압",
  11: "CO2",
  12: "EC",
  13: "광양자",
  14: "토양함수율",
  15: "토양수분장력",
  16: "pH",
  17: "지온",
  18: "무게"
  20: "암모니아",
  21: "조도",
  22: "차압",
  23: "일조",
  24: "정전",
  25: "누전",
  26: "아크",
  27: "낙뢰보호기",
  28: "산소",
  101: "레벨0스위치",
  102: "레벨1스위치",
  103: "레벨2스위치",
  111: "레벨0개폐기",
  112: "레벨1개폐기",
  113: "레벨2개폐기",
  201: "레벨0양액기",
  202: "레벨1양액기",
  203: "레벨2양액기",
  204: "레벨3양액기"
};

var testmanager = function () {
	var _scenarios = {
		"S.001": [{
				key: "NODE_CONN",
			}, {
				key: "NODE_INFO",
				param: [{
						values: [0, 0, 1, 0, 10, 30, "?", "?"]
			  }],
			}, {
				key: "DEV_INFO",
				param: [{
						length: 30,
						values: [ "!1", "!1", "!1", "!2", "!3", "!4", "!5", "!6", "!7", "!8", "!9", "!10", "!11", "!12", "!13", "!14", "!15", "!16", "!17", "!1", "!1", "!1", "!1", "!1", "!1", "!1", "!2", "!2", "!18", "!18"]
				}],
			}, {
				key: "NODE_STATUS",
			}, {
				key: "SENSOR_INFO",
			},
		],
		"S.005": [{       // 디폴트 축산 센서노드
				key: "NODE_CONN",
			}, {
				key: "NODE_INFO",
				param: [{
						values: [0, 0, 7, 1001, 10, 30, "?", "?"]
			  }],
			}, {
				key: "DEV_INFO",
				param: [{
						length: 30,
						values: [ "!1", "!1", "!1", "!2", "!2", "!2", "!11", "!20", "!21", "!28", "!22", "!8", "!1", "!2", "!9", "!8", "!4", "!7", "!23", "!20", "!24", "!25", "!26", "!27", 0, 0, 0, 0, 0, 0]
				}],
			}, {
				key: "NODE_STATUS",
			}, {
				key: "SENSOR_INFO",
			},
		],
		"S.002": [ {
				key: "NODE_CONN",
			}, {
				key: "NODE_INFO",
				param: [ {
						values: [0, 0, 2, 0, 10, 24, "?", "?"]
			  }]
			},
			{
				key: "DEV_INFO",
				param: [{
						length: 24,
						values: [ "!102", "!102", "!102", "!102", "!102", "!102", "!102", "!102", "!102", "!102", "!102", "!102", "!102", "!102", "!102", "!102", "!112", "!112", "!112", "!112", "!112", "!112", "!112", "!112"]
			  }]
			}, {
				key: "NODE_STATUS",
			}, {
				key: "ACTUATOR_INFO",
			}, {
				key: "SWITCH_LV1_ACT",
			}, {
				key: "RETRACTABLE_LV1_ACT",
			},
		],
		"S.003": [ {
				key: "CTRL_CONN",
			}, {
				key: "CTRL_SNODE",
			}, {
				key: "CTRL_SENSOR",
			},
		],
		"S.004": [ {
				key: "CTRL_CONN",
			}, {
				key: "CTRL_SNODE",
			}, {
				key: "CTRL_SENSOR",
			}, {
				key: "CTRL_ANODE",
			}, {
				key: "CTRL_SWITCH_LV1",
			}, {
				key: "CTRL_RETRACTABLE_LV1",
			},
		],
	};

	var _contents = {
		NODE_CONN: {
			name: "노드연결시험",
			process: [
				["confirm", "검정장비와 시험대상 노드 연결", "검정장비와 시험대상 노드를 RS485 케이블로 연결하였다."],
				[
					"confirm",
					"검정장비에 통신 설정값 셋팅",
					"시험대상 노드의 설정값을 확인하여 검정장비에 통신 설정값을 세팅하였다. (포트정보, 보레이트:9600)",
				],
				[
					"confirm",
					"검정장비에 슬레이브 아이디 입력",
					"검정장비에 시험대상 노드의 슬레이브 아이디를 입력하였다.",
				],
				["confirm", "검정장비와 대상장비 통신연결", "검정장비와 시험대상 장비의 통신이 연결되었다."],
			],
		},
		NODE_INFO: {
			name: "노드정보 확인시험",
			process: [
				/* values :  디폴트 센서노드라면.. [0, 0, 1, 0, 10, 30, "?", "?"] */
				["read_check", 1, 8, null, 2],
			],
		},
		DEV_INFO: {
			name: "노드에 연결된 장비 확인시험",
			process: [
				/* length :  디폴트 센서노드라면.. 30 */
				["read_check", 101, -1, null, 2],
			],
		},
		NODE_STATUS: {
			name: "노드 상태정보 확인시험",
			process: [["read_check", 202, 1, [0], 2]],
		},
		SENSOR_INFO: {
			name: "센서 정보 확인시험",
			process: [
				/* address : 디폴트 센서노드의 온도센서 #1이라면.. 203 */
				["read_check", -1, 3, ["?", "?", 0], 2],
				["read_confirm", -1, "센서값 확인", "센서관측치가 $f0 가 맞는지 확인하세요."],
			],
		},
		ACTUATOR_INFO: {
			name: "구동기 정보 확인시험",
			process: [
				/* address : 디폴트 구동기노드의 스위치 #1이라면.. 203 */
				["read_check", -1, 4, ["?", 0, 0, 0], 2],
			],
		},
		SWITCH_LV1_ACT: {
			name: "레벨 1 스위치 시험",
			process: [
				/* address : 디폴트 구동기노드의 스위치 #1이라면.. 503 */
				["write", -1, 4, [202, 100, 60, 0], 5],
				/* address : 디폴트 구동기노드의 스위치 #1이라면.. 203, 작동확인 */
				["read_check", -1, 4, [100, 201, "<60", 0], 5],
				["confirm", "스위치 작동여부 확인", "스위치가 1분동안 작동했다."],
				/* address : 디폴트 구동기노드의 스위치 #1이라면.. 203, 작동중지확인  */
				["read_check", -1, 4, [100, 0, 0, 0], 2],
				/* address : 디폴트 구동기노드의 스위치 #1이라면.. 503 */
				["write", -1, 4, [202, 101, 60, 0], 5],
				/* address : 디폴트 구동기노드의 스위치 #1이라면.. 203, 작동확인 */
				["read_check", -1, 4, [101, 201, "<60", 0], 15],
				/* address : 디폴트 구동기노드의 스위치 #1이라면.. 503 */
				["write", -1, 4, [0, 102, 0, 0], 5],
				/* address : 디폴트 구동기노드의 스위치 #1이라면.. 203, 작동중지확인 */
				["read_check", -1, 4, [102, 0, 0, 0], 5],
				["confirm", "스위치 작동여부 확인", "스위치가 20초동안 작동했다."],
			],
		},
		RETRACTABLE_LV1_ACT: {
			name: "레벨 1 개폐기 시험",
			process: [
				/* address : 디폴트 구동기노드의 개폐기 #1이라면.. 503 */
				["write", -1, 4, [303, 200, 60, 0], 5],
				/* address : 디폴트 구동기노드의 개폐기 #1이라면.. 203, 작동확인 */
				["read_check", -1, 4, [200, 301, "<60", 0], 5],
				["confirm", "개폐기 작동여부 확인", "개폐기가 1분동안 열리는 방향으로 작동했다."],
				/* address : 디폴트 구동기노드의 개폐기 #1이라면.. 203, 작동중지확인  */
				["read_check", -1, 4, [200, 0, 0, 0], 5],

				/* address : 디폴트 구동기노드의 개폐기 #1이라면.. 503 */
				["write", -1, 4, [304, 201, 60, 0], 5],
				/* address : 디폴트 구동기노드의 개폐기 #1이라면.. 203, 작동확인 */
				["read_check", -1, 4, [201, 302, "<60", 0], 5],
				["confirm", "개폐기 작동여부 확인", "개폐기가 1분동안 닫히는 방향으로 작동했다."],
				/* address : 디폴트 구동기노드의 개폐기 #1이라면.. 203, 작동중지확인  */
				["read_check", -1, 4, [201, 0, 0, 0], 5],

				/* address : 디폴트 구동기노드의 개폐기 #1이라면.. 503 */
				["write", -1, 4, [303, 202, 60, 0], 5],
				/* address : 디폴트 구동기노드의 개폐기 #1이라면.. 203, 작동확인 */
				["read_check", -1, 4, [202, 301, "<60", 0], 15],
				/* address : 디폴트 구동기노드의 개폐기 #1이라면.. 503 */
				["write", -1, 4, [0, 203, 0, 0], 5],
				/* address : 디폴트 구동기노드의 개폐기 #1이라면.. 203, 작동중지확인 */
				["read_check", -1, 4, [203, 0, 0, 0], 5],
				["confirm", "개폐기 작동여부 확인", "개폐기가 20초동안 열리는 방향으로 작동했다."],

				/* address : 디폴트 구동기노드의 개폐기 #1이라면.. 503 */
				["write", -1, 4, [304, 204, 60, 0], 5],
				/* address : 디폴트 구동기노드의 개폐기 #1이라면.. 203, 작동확인 */
				["read_check", -1, 4, [204, 302, "<60", 0], 15],
				/* address : 디폴트 구동기노드의 개폐기 #1이라면.. 503 */
				["write", -1, 4, [0, 205, 0, 0], 5],
				/* address : 디폴트 구동기노드의 개폐기 #1이라면.. 203, 작동중지확인 */
				["read_check", -1, 4, [205, 0, 0, 0], 5],
				["confirm", "개폐기 작동여부 확인", "개폐기가 20초동안 열리는 방향으로 작동했다."],
			],
		},
		CTRL_CONN: {
			name: "제어기연결시험",
			process: [
				[
					"confirm",
					"검정장비와 시험대상 제어기 연결",
					"검정장비와 시험대상 제어기를 RS485 케이블로 연결하였다.",
				],
				[
					"confirm",
					"검정장비에 통신 설정값 셋팅",
					"검정장비에 통신 설정값을 세팅하였다. (슬레이브아이디, 포트정보, 보레이트:9600)",
				],
				[
					"confirm",
					"제어기에 통신 설정값 세팅",
					"시험대상 제어기의 통신 설정값을 세팅하였다. (포트정보, 보레이트:9600)",
				],
				["confirm", "검정장비와 시험대상 제어기 통신연결", "검정장비와 시험대상 제어기의 통신이 연결되었다."],
			],
		},
		CTRL_SNODE: {
			name: "제어기 센서노드 연동 시험",
			process: [
				["set", 1, 8, [0, 0, 1, 0, 10, 30, 0, 0], 2],
				[
					"set",
					101,
					30,
					[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
					2,
				],
				["set", 202, 1, [0], 2],
				["confirm", "제어기 센서노드검색", "제어기에서 센서노드가 검색되었다."],
				["confirm", "센서노드에 연결된 센서", "검색된 센서노드에는 연결된 센서가 없다."],
				["set", 202, 1, [1], 2],
				["confirm", "센서노드 확인", "센서노드가 비정상으로 변경되었다."],
			],
		},
		CTRL_SENSOR: {
			name: "제어기 센서노드 데이터 시험",
			process: [
				["set", 1, 8, [0, 0, 1, 0, 10, 30, 0, 0], 2],
				[
					"set",
					101,
					30,
					[1, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
					2,
				],
				["set", 202, 1, [0], 2],
				["set", 203, 3, [26214, 16870, 0], 2],
				["set", 212, 3, [26214, 17069, 0], 2],
				["confirm", "제어기 센서노드검색", "제어기에서 센서노드가 검색되었다."],
				[
					"confirm",
					"센서노드에 연결된 센서",
					"검색된 센서노드에는 온도센서와 습도센서가 각각 1개씩 연결되었다.",
				],
				["confirm", "온도센서 확인", "검색된 온도센서는 정상이며, 관측된 온도는 28.8도이다."],
				["confirm", "습도센서 확인", "검색된 습도센서는 정상이며, 관측된 습도는 86.7%이다. "],
				["set", 203, 3, [26214, 17069, 1], 5],
				["set", 212, 3, [26214, 17056, 1], 5],
				["confirm", "온도센서 확인", "온도센서는 비정상이며, 관측된 온도는 86.7도이다."],
				["confirm", "습도센서 확인", "습도센서는 비정상이며, 관측된 습도는 80.2%이다."],
			],
		},
		CTRL_ANODE: {
			name: "제어기 구동기노드 연동 시험",
			process: [
				["set", 1, 8, [0, 0, 2, 0, 10, 24, 0, 0], 2],
				["set", 101, 24, [0, 102, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 112, 0, 0, 0, 0, 0, 0], 2],
				["set", 202, 1, [0], 2],
				["set", 207, 4, [0, 0, 0, 0], 2],
				["set", 271, 4, [0, 0, 0, 0], 2],
				["confirm", "제어기 구동기노드검색", "제어기에서 구동기노드가 검색되었다."],
				[
					"confirm",
					"구동기노드에 연결된 구동기",
					"검색된 구동기노드에는 스위치와 개폐기가 각각 1개씩 연결되었다.",
				],
				["confirm", "구동기노드 확인", "검색된 구동기노드가 정상이다."],
			],
		},
		CTRL_SWITCH_LV1: {
			name: "제어기 레벨1 스위치제어 시험",
			process: [
				["set", 1, 8, [0, 0, 2, 0, 10, 24, 0, 0], 2],
				["set", 101, 24, [0, 102, 102, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 2],
				["set", 202, 1, [0], 2],
				["set", 207, 4, [0, 0, 0, 0], 2],
				["set", 211, 4, [0, 0, 0, 0], 2],
				["confirm", "제어기 구동기노드검색", "제어기에서 구동기노드가 검색되었다."],
				["confirm", "구동기노드에 연결된 구동기", "검색된 구동기노드에는 스위치가 2개(2, 3번채널) 연결되었다."],
				["confirm", "스위치 확인", "검색된 스위치는 중지상태이다."],
				["confirm", "스위치 구동명령 확인", "2번채널 스위치에 30초간 작동명령을 내리고, 확인을 누르세요."],
				["scan_check", 507, 4, [202, "?", 30, 0], 5],
				["scan_set", 207, 4, 507, ["$1", 202, 25, 0], 5],
				["set", 209, 2, [20, 0], 5],
				["set", 209, 2, [15, 0], 5],
				["set", 209, 2, [10, 0], 5],
				["set", 209, 2, [5, 0], 5],
				["set", 208, 3, [0, 0, 0], 5],
				[
					"confirm",
					"스위치 구동명령 확인",
					"2번채널 스위치가 작동되었다고 표시되었고,  남은동작시간이 점차 줄어들었으며, 30초 정도 동작하고 정지된 것으로 표시되었다.",
				],
				["confirm", "스위치 구동명령 확인", "2번채널 스위치에 30초간 작동명령을 내리고, 확인을 누르세요."],
				["scan_check", 507, 4, [202, "?", 30, 0], 5],
				["scan_set", 207, 4, 507, ["$1", 202, 25, 0], 5],
				["set", 209, 2, [20, 0], 5],
				["set", 209, 2, [15, 0], 5],
				["confirm", "스위치 정지명령 확인", "2번채널 스위치에 정지명령을 내리세요."],
				["scan_check", 507, 4, [0, "?", 0, 0], 5],
				["scan_set", 207, 4, 507, ["$1", 0, 0, 0], 5],
				["confirm", "스위치 정지명령 확인", "2번채널 스위치가 정지된 것으로 표시되었다."],
			],
		},
		CTRL_RETRACTABLE_LV1: {
			name: "제어기 레벨1 개폐기제어 시험",
			process: [
				["set", 1, 8, [0, 0, 2, 0, 10, 24, 0, 0], 2],
				["set", 101, 24, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 112, 112, 0, 0, 0, 0, 0, 0], 2],
				["set", 202, 1, [0], 2],
				["set", 267, 4, [0, 0, 0, 0], 2],
				["set", 271, 4, [0, 0, 0, 0], 2],
				["confirm", "제어기 구동기노드검색", "제어기에서 구동기노드가 검색되었다."],
				["confirm", "구동기노드에 연결된 구동기", "검색된 구동기노드에는 개폐기가 2개(1,2채널) 연결되었다."],
				["confirm", "구동기노드 확인", "검색된 구동기노드가 정상이다."],
				["confirm", "개폐기 확인", "검색된 개폐기는 중지상태이다."],
				["confirm", "개폐기 열림명령 확인", "1채널 개폐기에 30초간 열림명령을 내리고, 확인을 누르세요."],
				["scan_check", 567, 4, [303, "?", 30, 0], 5],
				["scan_set", 267, 4, 567, ["$1", 301, 25, 0], 5],
				["set", 269, 2, [20, 0], 5],
				["set", 269, 2, [15, 0], 5],
				["set", 269, 2, [10, 0], 5],
				["set", 269, 2, [5, 0], 5],
				["set", 268, 3, [0, 0, 0], 5],
				[
					"confirm",
					"개폐기 열림명령 확인",
					"1채널 개폐기가 열린다고 표시되었고,  남은동작시간이 점차 줄어들었으며, 30초 정도 동작하고 정지된 것으로 표시되었다.",
				],
				["confirm", "개폐기 닫힘명령 확인", "1채널 개폐기에 30초간 닫힘명령을 내리고, 확인을 누르세요."],
				["scan_check", 567, 4, [304, "?", 30, 0], 5],
				["scan_set", 267, 4, 567, ["$1", 302, 25, 0], 5],
				["set", 269, 2, [20, 0], 5],
				["set", 269, 2, [15, 0], 5],
				["set", 269, 2, [10, 0], 5],
				["set", 269, 2, [5, 0], 5],
				["set", 268, 3, [0, 0, 0], 5],
				[
					"confirm",
					"개폐기 닫힘명령 확인",
					"1채널 개폐기가 닫힌다고 표시되었고,  남은동작시간이 점차 줄어들었으며, 30초 정도 동작하고 정지된 것으로 표시되었다.",
				],
				// [
				//     "confirm",
				//     "스위치 구동명령 확인",
				//     "스위치에 30초간 작동명령을 내리고, 확인을 누르세요.",
				// ],
				// ["scan_check", 507, 4, [202, "?", 30, 0], 5],
				// ["scan_set", 207, 4, 507, ["$1", 202, 25, 0], 5],
				// ["set", 209, 2, [20, 0], 5],
				// ["set", 209, 2, [15, 0], 5],
				// [
				//     "confirm",
				//     "스위치 정지명령 확인",
				//     "스위치에 정지명령을 내리세요.",
				// ],
				// ["scan_check", 507, 4, [0, "?", 0, 0], 5],
				// ["scan_set", 207, 4, 507, ["$1", 0, 0, 0], 5],
				// [
				//     "confirm",
				//     "스위치 구동명령 확인",
				//     "스위치가 정지된 것으로 표시되었다.",
				// ],
			],
		},
	};

	/**
	 * @method _makeprocess
	 * @description 컨텐츠내 프로세스를 만들어냅니다.
	 */
	var _makeprocess = function (proc, param) {
		process = null;
		switch (proc[0]) {
			case "confirm":
				process = {
					command: proc[0],
					param: { title: proc[1], message: proc[2] },
				};
				break;
			case "read_confirm":
				process = {
					command: proc[0],
					// param: { from: proc[1], title: proc[2], message: proc[3] },
					param: {
						title: proc[2],
						message: proc[3],
						from: param.address,
					},
				};
				break;
			case "read":
			case "scan":
				process = {
					command: proc[0],
					param: { address: proc[1], length: proc[2] },
					delay: proc[3],
				};
				break;
			case "set":
			case "read_check":
			case "scan_check":
			case "write":
				process = {
					command: proc[0],
					param: {
						address: proc[1],
						length: proc[2],
						values: proc[3],
					},
					delay: proc[4],
				};
				break;
			case "scan_set":
				process = {
					command: proc[0],
					param: {
						address: proc[1],
						length: proc[2],
						from: proc[3],
						values: proc[4],
					},
					delay: proc[5],
				};
				break;
		}

		if (process == null) {
			console.log("unknown command : " + proc);
			return {};
		} else if (param != null) {
			if (process.command !== "read_confirm") {
				for (var key in param) {
					process["param"][key] = param[key];
				}
			}
		}
		return process;
	};

	/**
	 * @method _makecontent
	 * @description 컨텐츠를 신규로 만들어냅니다.
	 */
	var _makecontent = function (key, id, params, dev_type, dev_info) {
		console.log("make content", key, id);

		var target = dev_type;
		switch (dev_type) {
			case "003":
				if (key == "CTRL_SNODE" || key == "CTRL_SENSOR") {
					target = "001";
				}
				break;
			case "004":
				if (key == "CTRL_SNODE" || key == "CTRL_SENSOR") {
					target = "001";
				} else if (key == "CTRL_ANODE" || key == "CTRL_SWITCH_LV1" || key == "CTRL_RETRACTABLE_LV1") {
					target = "002";
				} else if (key == "CTRL_CONN") {
					console.log("CTRL_CONN");
					target = "004";
				}
				break;
			default:
				break;
		}

		if (key == "SENSOR_INFO") {
			const id_str = id.split("-");
			for (var i = 0; i < dev_info.length; i++) {
        if (dev_info[i] == 0 || dev_info[i] > 100) {
          // no need to check
          continue;
        }

        if (dev_info[i] in devnames) {
				  _contents[key].name = devnames[dev_info[i]] + "센서 정보 확인시험";
        } else {
				  _contents[key].name = "알려지지 않은 (" + dev_info[i] + ") 센서 정보 확인시험";
        }
			}
		}
		console.log("target");
		console.log(target);
		newcontent = { target: target, key: key, id: id };
		Object.assign(newcontent, _contents[key]);
		newcontent["process"] = [];
		proc = _contents[key]["process"];
		if (params != null) {
			for (var i = 0; i < proc.length; i++) {
				newcontent["process"].push(_makeprocess(proc[i], params[i]));
			}
		} else {
			for (var i = 0; i < proc.length; i++) {
				newcontent["process"].push(_makeprocess(proc[i], null));
			}
		}

		return newcontent;
	};

	/**
	 * @method _makeSIcontent
	 * @description SENSOR_INFO의 컨텐츠를 신규로 만들어냅니다.
	 */
	var _makeSIcontent = function (scenario, dev_type, dev_info) {
		return _makeSIAIcontent(scenario, 3, dev_type, dev_info);
	};

	/**
	 * @method _makeAIcontent
	 * @description ACTUATOR_INFO의 컨텐츠를 신규로 만들어냅니다.
	 */
	var _makeAIcontent = function (scenario, dev_type, dev_info) {
		return _makeSIAIcontent(scenario, 4, dev_type, dev_info);
	};

	/**
	 * @method _finddevinforesult
	 * @description 시나리오에서 DEV_INFO 시험 결과를 찾습니다.
	 */
	var _finddevinforesult = function (scenario) {
		for (var test of scenario["schema"]) {
			if (test["key"] == "DEV_INFO") {
				if ("result" in test && Array.isArray(test["result"]) && "values" in test["result"][0])
					return test["result"][0]["values"];
				throw new Error("Devinfo doesnt have a result.");
			}
		}
		throw new Error("Fail to find devinfo.");
	};

	/**
	 * @method _makeSIAIcontent
	 * @description SENSOR_INFO, ACTUATOR_INFO의 컨텐츠를 신규로 만들어냅니다.
	 */
	var _makeSIAIcontent = function (scenario, step, dev_type, dev_info) {
		console.log("_makeSIAIcontent");
		try {
			const idx = scenario["idx"];
			const schema = scenario["schema"];
			const key = schema[idx]["key"];

			devinfo = _finddevinforesult(scenario);

			params = [{ address: 0 }, { address: 0 }];
			content = [];

			for (var i = 0; i < devinfo.length; i++) {
				if (devinfo[i] == 0) {
					continue;
				}
				params[0]["address"] = 203 + i * step;
				params[1]["address"] = 203 + i * step; // AI의 경우에는 불필요함.
				content.push(_makecontent(key, key + "-" + i, params, dev_type, dev_info));
			}
			return content;
		} catch (error) {
			console.log(error);
		}
	};

	/**
	 * @method _makeSWCL1content
	 * @description 레벨1 스위치를 위한 컨텐츠를 만든다.
	 */
	var _makeSWCL1content = function (scenario, dev_type, dev_info) {
		console.log("_makeSWCL1content");
		return _makeACTL1content(scenario, 102, dev_type, dev_info);
	};

	/**
	 * @method _makeRETL1content
	 * @description 레벨1 개폐기를 위한 컨텐츠를 만든다.
	 */
	var _makeRETL1content = function (scenario, dev_type, dev_info) {
		console.log("_makeRETL1content");
		return _makeACTL1content(scenario, 112, dev_type, dev_info);
	};

	/**
	 * @method _makeACTL1content
	 * @description 레벨1 구동기를 위한 컨텐츠를 만든다.
	 */
	var _makeACTL1content = function (scenario, devcode, dev_type, dev_info) {
		console.log("_makeACTL1content", devcode);

		const idx = scenario["idx"];
		const schema = scenario["schema"];
		const key = schema[idx]["key"];

		devinfo = _finddevinforesult(scenario);

		content = [];
		const procs = _contents[key]["process"];
		for (var i = 0; i < devinfo.length; i++) {
			if (devinfo[i] == 0 || devinfo[i] != devcode) continue;
			params = [];
			for (var j = 0; j < procs.length; j++) {
				var proc = procs[j];
				if (proc[0] == "write") {
					tmp = { address: 503 + i * 4 };
				} else if (proc[0] == "read_check") {
					tmp = { address: 203 + i * 4 };
				} else {
					tmp = {};
				}
				params.push(tmp);
			}
			content.push(_makecontent(key, key + "-" + i, params, dev_type, dev_info));
		}
		console.log("_makeACTL1content", devcode, content);
		return content;
	};

	/**
	 * @method newScenarioSchema
	 * @description 대상장비의 시나리오 골격을 리턴한다.
	 */
	var newScenarioSchema = function (code) {
		console.log("newScenarioSchema : " + "S." + code);
		return { idx: 0, schema: _scenarios["S." + code] };
	};

	/**
	 * @method generateContent
	 * @description 시나리오 골격과 이전 응답을 이용하여 다음 시나리오 컨텐츠를 생성한다.
	 */
	var generateContent = function (scenario, dev_type, dev_info) {
		console.log("generateContent");
		const idx = scenario["idx"];
		const schema = scenario["schema"];

		if (isDone(scenario) == true) {
			console.log("The", idx, "test finished.");
			throw new Error("Test finished.");
		}

		const key = schema[idx]["key"];

		if ("name" in schema[idx]) {
			console.log("A content was already made.");
			return scenario;
		}

		if ("param" in schema[idx]) params = schema[idx]["param"];
		else params = null;

		functbl = {
			SENSOR_INFO: _makeSIcontent,
			ACTUATOR_INFO: _makeAIcontent,
			SWITCH_LV1_ACT: _makeSWCL1content,
			RETRACTABLE_LV1_ACT: _makeRETL1content,
		};

		if (key in functbl) {
			if (functbl[key](scenario, dev_type, dev_info)) {
				schema.splice(idx, 1, ...functbl[key](scenario, dev_type, dev_info));
			}
		} else {
			schema[idx] = _makecontent(key, key, params, dev_type, dev_info);
		}
		return scenario;
	};

	/**
	 * @method isDone
	 * @description 대상장비의 시험이 끝났는지를 확인한다.
	 */
	var isDone = function (scenario) {
		const idx = scenario["idx"];
		const schema = scenario["schema"];

		if (idx >= schema.length) {
			return true;
		} else {
			return false;
		}
	};

	/**
	 * @method _checkDIresult
	 * @description 장비 정보의 결과가 맞는지 확인합니다.
	 */
	var _checkDIresult = function (schema, result) {
		console.log("_checkDIresult");
		if (result[0]["result"] == "success") return null;
		return {
			result: "fail",
			message: name + "결과 장비코드가 적절하지 않습니다. " + JSON.stringify(result[0]["values"]),
		};
	};

	/**
	 * @method _checkresult
	 * @description 대상장비의 컨텐츠 시험결과를 확인하고, 결과를 리턴한다.
	 */
	var _checkresult = function (schema, result) {
		const key = schema["key"];
		const id = schema["id"];
		const name = schema["name"];
		const process = schema["process"];

		schema["result"] = result;

		if (process.length != result.length)
			return {
				result: "fail",
				message: "컨텐츠와 결과물의 길이가 일치하지 않습니다. 검증장비 오류로 보이니 확인이 필요합니다.",
			};

		const functbl = {
			DEV_INFO: _checkDIresult,
		};

		if (key in functbl) {
			ret = functbl[key](schema, result);
			if (ret != null) return ret;
		} else {
			for (var ret of result) {
				if (ret["result"] == "success") continue;
				return {
					result: "fail",
					message: name + "에서 성공하지 못한 내용이 있습니다.",
				};
			}
		}
		return {
			result: "success",
			message: name + "이 정상적으로 종료되었습니다.",
		};
	};

	/**
	 * @method setContentResult
	 * @description 대상장비의 컨텐츠 시험결과를 업데이트 한다.
	 */
	var setContentResult = function (scenario, id, result) {
		console.log("setContentResult");

		const schema = scenario["schema"];
		var idx = scenario["idx"];

		if (id == schema[idx]["id"]) {
			console.log(schema[idx]);
			schema[idx]["decision"] = _checkresult(schema[idx], result);
			const key = schema[idx]["key"];
			scenario["idx"] = idx + 1;
		} else {
			// 아이디가 다르다면 재시험을 하는 경우이다.
			for (var i = 0; i < idx; i++) {
				if (schema[i]["id"] == id) {
					console.log("Test Again", id);
					schema[i]["decision"] = _checkresult(schema[i], result);
				}
			}
		}

		return scenario;
	};

	var _descriptions = {
		NODE_CONN: "검정장비와 시험대상 노드가 정상적으로 통신 연결이 이루어지는지 시험합니다.",
		NODE_INFO: "노드정보 영역에 노드 정보가 올바르게 기록되어 있는지 확인합니다.",
		DEV_INFO: "노드에 연결된 장비들의 코드가 올바르게 기록되어 있는지 확인합니다.",
		NODE_STATUS: "노드의 상태값이 정상인지를 확인합니다.",
		SENSOR_INFO: "연결된 센서의 상태가 정상이고, 관측치를 전달할 수 있는지 확인합니다.",
		ACTUATOR_INFO: "연결된 구동기의 상태가 정상인지를 확인합니다.",
		SWITCH_LV1_ACT: "연결된 레벨 1 스위치가 정상적으로 작동하는지 확인합니다.",
		RETRACTABLE_LV1_ACT: "연결된 레벨 1 개폐기가 정상적으로 작동하는지 확인합니다.",
		CTRL_CONN: "검정장비와 시험대상 제어기가 정상적으로 통신 연결이 이루어지는지 시험합니다.",
		CTRL_SNODE: "시험대상 제어기가 센서노드의 상태를 확인할 수 있는지 시험합니다.",
		CTRL_SENSOR: "시험대상 제어기가 센서노드에 연결된 센서의 상태와 관측치를 확인할 수 있는지 시험합니다.",
		CTRL_ANODE: "시험대상 제어기가 구동기노드의 상태를 확인할 수 있는지 시험합니다.",
		CTRL_SWITCH_LV1: "시험대상 제어기가 레벨 1 스위치를 정상적으로 제어할 수 있는지 시험합니다.",
		CTRL_RETRACTABLE_LV1: "시험대상 제어기가 레벨 1 개폐기를 정상적으로 제어할 수 있는지 시험합니다.",
	};

	/**
	 * @method getScenarioSchema
	 * @description 대상 장비의 종류에 따라서 실행할 시험에 대한 템플릿 정보를 제공한다.
	 */
	var getScenarioSchema = function (code) {
		schema = _scenarios["S." + code];
		for (var test of schema) {
			key = test["key"];
			test["name"] = _contents[key]["name"];
			test["description"] = _descriptions[key];
			delete test.param;
		}
		return schema;
	};

	/**
	 * @method generateReport
	 * @description 대상장비에 대한 시험결과 리포트를 생성한다.
	 */
	var generateReport = function (scenario) {
		const schema = scenario["schema"];
		const idx = scenario["idx"];

		if (isDone(scenario) == false) {
			console.log("Test is not finished yet.");
			throw new Error("Test is not finished yet.");
		}

		report = [];
		for (var content of schema) {
			item = {
				name: content.name,
				description: _descriptions[content.key],
				decision: content.decision,
				detail: [],
				logs: [],
			};
			for (var i = 0; i < content.process.length; i++) {
				console.log(
					content.process[i].command,
					["confirm", "read_confirm"].includes(content.process[i].command)
				);
				if (["confirm", "read_confirm"].includes(content.process[i].command) == true) {
					item.detail.push({
						message: content.process[i].param.message,
						result: content.result[i].result,
					});
				}
				item.logs.push({
					process: content.process[i],
					result: content.result[i],
				});
			}
			report.push(item);
		}

		return report;
	};

	function findUserAndCallBack(cb) {
		return new Promise(function (resolve, reject) {
			const _query = "select * from exam_scenario where device_id = '996' ";
			_pool.getConnection(function (err, conn) {
				console.log(err);
				console.log(conn);
				if (!err) {
					console.log("연결 성공");
					const [rows] = conn.query(_query);
					console.log(rows);
				}
				conn.release();
				global_rows = rows;
				resolve(rows);
			});
			// const _query = "select * from exam_scenario where device_id = '996' ";
			// const [rows] = await _pool.query(_query)
			// return rows
		});
	}

	function func1() {
		return new Promise(resolve => {
			const player = {
				name: "mason mount",
				age: 22,
				number: 33,
				position: "midfielder",
			};
			resolve(player);
		});
	}

	function eat(vegetable) {
		console.log(`fruit: ${global_rows} / vegetable: ${vegetable}`);
		var obj = {};
		obj.vegetable = `${vegetable}`;
		return obj;
	}

	return {
		newScenarioSchema: newScenarioSchema,
		generateContent: generateContent,
		isDone: isDone,
		setContentResult: setContentResult,
		generateReport: generateReport,
		getScenarioSchema: getScenarioSchema,
	};
};

module.exports = testmanager();
