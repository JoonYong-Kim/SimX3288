/**
 * @fileoverview SimX UI Action Javascript API
 * @author tombraid@snu.ac.kr
 * @version 0.1.0
 * @since 2023.05.03
 */

var SimXAct = function (ui, comm) {
  _ui = ui;
  _comm = comm;

  var modechange = function (mode) {
    console.log("mode change : " + mode);
    $.post("/modechange", {"mode":mode}, function(param) { console.log ("sent"); }, 'json')
      .done(function(param) { console.log ("changed. wait for a while"); })
      .fail(function(param) { console.log ("fail to mode change"); })
      .always(function(param) { _ui.reset(); });
  }

  var getmode = function() {
  }

  var setcontrol = function (control) {
    _comm.control(control);
  }

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
      modechange(this.value);
    });
    $("input[name='control']:radio").change (function () {
      console.log("control : " + this.value);
      setcontrol(this.value);
    });
    $("input[name='command']:radio").change (function () {
      console.log("command : " + this.value);
      setcommand(this.value);
    });
  }

  return {
    setAction: setAction
  }
}

//module.exports = SimXUI();

