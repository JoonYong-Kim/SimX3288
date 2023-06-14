/**
 * @fileoverview SimX UI Action Javascript API
 * @author tombraid@snu.ac.kr
 * @version 0.1.0
 * @since 2023.05.03
 */

var SimXAct = function (ui, comm) {
  _ui = ui;
  _comm = comm;

  var setcommand = function (cmd) {
    if (cmd == 0) {
      _comm.stop();

    } else if (cmd == 401) {
      _comm.once();

    } else if (cmd == 402) {
      _comm.irrigate( $("input[name='on-sec']").val(), 
        $("input[name='start-area']").val(), $("input[name='stop-area']").val());

    } else if (cmd == 403) {
      _comm.fertigate( $("input[name='on-sec']").val(), 
        $("input[name='start-area']").val(), $("input[name='stop-area']").val(),
        $("input[name='EC']").val(), $("input[name='pH']").val());

    } else {
      console.log ("unknown command : " + cmd);
    }
  }

  var setAction = function() {
    $("input[name='mode']:radio").change (function () {
      console.log("mode change : " + this.value);
      _ui.confirmdlg("작동모드 변경", "작동모드를 변경하시겠습니까?", this.value, function(mode) {
        _comm.modechange(mode);
      }, function () {
        // 작동모드 선택 원래대로.
      });
    });

    $(".ctrlbtn").click(function () {
      console.log("control : " + $(this).attr('control'));
      _ui.confirmdlg("제어권 변경", "제어권을 변경하시겠습니까?", $(this).attr('control'), function(control) {
        _comm.control(control);
      }, function () {
        // 제어권 선택 원래대로.
      });
    });

    /*
    $("input[name='command']:radio").change (function () {
      console.log("command : " + this.value);
      setcommand(this.value);
    });
    */
    $(".cmdbtn").click (function () {
      console.log("command : " + $(this).attr('name'));
      _ui.confirmdlg("명령실행", "명령을 실행하시겠습니까?", $(this).attr('cmd'), function(cmd) {
        setcommand(cmd);
      }, function () {
      });
    });
  }

  return {
    setAction: setAction
  }
}

//module.exports = SimXUI();

