/**
 * @fileoverview SimX Communcation Javascript API
 * @author tombraid@snu.ac.kr
 * @version 0.1.0
 * @since 2023.05.03
 */

var SimXComm = function (host, ui) {
  var _host = host;
  var _opid = 1;
  var _mode = 0;
  var _ui = ui;
  var _cnt = 1;
  var _client = mqtt.connect("ws://" + host + ":9001", 
    {clean: true, connectTimeout: 4000, clientId: 'simx'});
  
  var initialize = function () {
    _client.on('connect', function () {
      console.log('Connected');
      _client.subscribe('simx/reg', function (err) {
        if (!err) {
          console.log('Subscribed : simx/reg');
        }
      });

      _client.subscribe('simx/res', function (err) {
        if (!err) {
          console.log('Subscribed : simx/res');
        }
      });

      _client.subscribe('ns2023/log', function (err) {
        if (!err) {
          console.log('Subscribed : ns2023/log');
        }
      });

    });

    _client.on('message', function (topic, payload) {
      // message is Buffer
      if (topic == "simx/res") {
        console.log("write result : " + payload.toString());
      } else if (topic == "simx/reg") {
        message = JSON.parse(payload.toString()) 
        if (message["addr"] == 1) {
          _ui.setNI(message["ret"][0], message["ret"][1], _mode);
        } else if (message["addr"] == 101) {
          _ui.setDI(message["ret"][0], message["ret"][1], _mode);
        } else if (message["addr"] == 201) {
          _ui.setNDS(message["ret"][0], message["ret"][1], _mode);
        } else if (message["addr"] == 204) {
          _ui.setSS(message["ret"][0], message["ret"][1], _mode);
        } else if (message["addr"] == 401) {
          _ui.setNSS(message["ret"][0], message["ret"][1], _mode);
        } else if (message["addr"] == 501) {
          if (message["ret"][0] == null)
            _ui.setNDC(message["ret"][1], _mode);
          else
            _ui.setNDC(message["ret"][0], _mode);
        } else if (message["addr"] == 504) {
          if (message["ret"][0] == null)
            _ui.setNSC(message["ret"][1], _mode);
          else
            _ui.setNSC(message["ret"][0], _mode);
        } else {
          console.log("unknown info" + payload.toString());
        }
      } else if (topic == "ns2023/log") {
        console.log(topic + " : " + payload.toString());
      }
    });
  }

  var updateinfo = function () {
    unit = $("input[name='unit']").val();
    if (_cnt % 5 == 1) {
      read(1, 8, unit);
      read(101, 21, unit);
    }

    read(501, 3, unit);
    read(504, 10, unit);

    read(201, 3, unit);
    read(204, 60, unit);
    read(401, 6, unit);

    getmode();
    _cnt++;
  }

  var setmode = function(mode) {
    //console.log("setmode : " + mode["real"] + " " + mode["ui"]);
    _mode = mode["real"];
    _ui.updatemodedesc(mode);
  }

  var getopid = function() {
    _opid += 1;
    if (_opid > 60000)
      _opid = 1;
    return _opid;
  }

  var read = function(addr, count, unit) {
    msg = {"addr":addr, "count":count, "unit":parseInt(unit)};
    _client.publish('simx/read', JSON.stringify(msg));
  }

  var write = function(addr, content, unit) {
    msg = {"addr":addr, "content":content, "unit":parseInt(unit)};
    _client.publish('simx/write', JSON.stringify(msg));
  }

  var control = function(control) {
    unit = $("input[name='unit']").val();
    write(501, [2, getopid(), parseInt(control)], unit);
  }

  var stop = function() {
    unit = $("input[name='unit']").val();
    write(504, [0, getopid()], unit);
  }

  var once = function() {
    unit = $("input[name='unit']").val();
    write(504, [401, getopid()], unit);
  }

  var irrigate = function(time, start, stop) {
    unit = $("input[name='unit']").val();
    ttime = packint(parseInt(time));
    write(504, [402, getopid(), parseInt(start), parseInt(stop), ttime[0], ttime[1]], unit);
  }

  var fertigate = function(time, start, stop, ec, ph) {
    unit = $("input[name='unit']").val();
    ttime = packint(parseInt(time));
    tec = packfloat(parseFloat(ec));
    tph = packfloat(parseFloat(ph));
    write(504, [403, getopid(), parseInt(start), parseInt(stop), ttime[0], ttime[1], tec[0], tec[1], tph[0], tph[1]], unit)
  }

  var packfloat = function(val) {
    var buf = new ArrayBuffer(4);
    var buf16 = new Uint16Array(buf);
    var num = new Float32Array(buf);
    num[0] = val;
    return [buf16[0], buf16[1]];
  }

  var packint = function(val) {
    var buf = new ArrayBuffer(4);
    var buf16 = new Uint16Array(buf);
    var num = new Int32Array(buf);
    num[0] = val;
    return [buf16[0], buf16[1]];
  }

  var modechange = function (mode) {
    console.log("mode change : " + mode);
    $.post("/modechange", {"mode":mode}, function(param) { /* console.log ("sent")*/; }, 'json')
      .done(function(param) { /*console.log ("changed. wait for a while")*/; })
      .fail(function(param) { /*console.log ("fail to mode change")*/; })
      .always(function(param) { ; });
  }

  var getmode = function() {
    $.get("/mode", function(param) { /* console.log ("sent")*/; })
      .done(function(param) { /* console.log (param)*/; setmode(JSON.parse(param)); })
      .fail(function(param) { /* console.log ("fail to mode change")*/; })
      .always(function(param) { ; });
  }

  var reset = function () {
    console.log("reset")
    $.get("/reset", function(param) { /* console.log ("sent")*/; })
      .done(function(param) { /*console.log ("reset. wait for a while")*/; })
      .fail(function(param) { /*console.log ("fail to reset")*/; })
      .always(function(param) { ; });
  }

  var reboot = function () {
    console.log("reboot")
    $.get("/reboot", function(param) { /* console.log ("sent")*/; })
      .done(function(param) { /*console.log ("reset. wait for a while")*/; })
      .fail(function(param) { /*console.log ("fail to reset")*/; })
      .always(function(param) { ; });
  }

  var halt = function () {
    console.log("halt")
    $.get("/halt", function(param) { /* console.log ("sent")*/; })
      .done(function(param) { /*console.log ("reset. wait for a while")*/; })
      .fail(function(param) { /*console.log ("fail to reset")*/; })
      .always(function(param) { ; });
  }

  var upgrade = function () {
    console.log("upgrade")
    $.get("/upgrade", function(param) { /* console.log ("sent")*/; })
      .done(function(param) { /*console.log ("reset. wait for a while")*/; })
      .fail(function(param) { /*console.log ("fail to reset")*/; })
      .always(function(param) { ; });
  }

  var setalert= function (alt) {
    console.log("setalert : " + alt)
    $.post("/setalert", {"alert":alt}, function(param) { /* console.log ("sent")*/; }, 'json')
      .done(function(param) { /*console.log ("reset. wait for a while")*/; })
      .fail(function(param) { /*console.log ("fail to reset")*/; })
      .always(function(param) { ; });
  }

  return {
    initialize: initialize,
    setmode: setmode,
    updateinfo: updateinfo,
    modechange: modechange,
    getmode: getmode,
    control: control,
    stop: stop,
    once: once,
    irrigate: irrigate,
    fertigate: fertigate,
    reset: reset,
    reboot: reboot,
    halt: halt,
    upgrade: upgrade,
    setalert: setalert
  };
}

//module.exports = SimXComm();

