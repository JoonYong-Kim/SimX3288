/**
 * @fileoverview SimX Tester Javascript API
 * @author tombraid@snu.ac.kr
 * @version 0.1.0
 * @since 2024.01.17
 *
 * 표준 적합성 시험을 위한 클래스
 */

var SimXTester = function () {

  var setVersion = function() {
      $("#ver").text("시뮬레이터 버전은 1.0.7 입니다.");
  }

  return {
    setNI: setNI,
    setDI: setDI,
    setNDC: setNDC,
    setNDS: setNDS,
    setNSC: setNSC,
    setNSS: setNSS,
    setSS: setSS,
    confirmdlg: confirmdlg,
    setVersion: setVersion,
    updatemodedesc: updatemodedesc
  }
}

//module.exports = SimXTester();

