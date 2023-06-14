#  Nutrient Supply Commnicator (nscomm)

## Introduction

NSComm 라이브러리는 양액기 표준 통신을 지원하기위한 python 라이브러리로 사용자가 쉽게 표준 통신을 수행할 수 있도록 돕습니다.

NSComm 라이브러리의 전체적인 구조는 아래와 같습니다. 사용자의 프로그램은 NSComm 을 활용해서 모드버스 슬레이브로 동작하고, 통합제어기(FarmOS)는 모드버스 마스터로 동작하게 됩니다

![구성](/imgs/structure.png)

## Environment

본 라이브러리는 아래의 환경에서 테스트 되었습니다.

* OS : Linux
* Language : Python 3.7, 3.8
* Package : pymodbus twisted enum34

Python 3.7의 경우 프로세스모드에서 정상작동을 하지 않습니다. 활용에 참고하세요.


## Installation

폴더에 있는 nscomm 폴더를 양액기 개발중인 폴더로 복사하면 됩니다.

만약 개발중인 폴더가 /home/pi/nutrientsupply 이고, 현재 디렉토리가 /home/pi/nscomm 이라면 다음과 같은 명령을 사용하면 됩니다.

```
cp -r nscomm /home/pi/nutrientsupply/
```

리눅스 사용에 좀더 익숙하다면 `ln -s` 명령을 사용하시면 더 좋습니다.

## Usage 

라이브러리의 상세한 사용법을 알고 싶으시다면, docs 폴더에 있는 [매뉴얼](/docs/manual.pdf) 문서를 참고하세요.

## References

* KS X 3267 : “스마트 온실 센서/구동기 노드 및 온실 통합 제어기간 RS485 기반 모드버스 인터페이스”
* KS 신규 : “스마트 온실의 온실 통합 제어기와 양액기 노드 간 RS485 기반 모드버스 인터페이스”
* KS 신규 : “RS485/모드버스 기반 스마트 온실 노드/디바이스 등록 절차 및 기술 규격”


