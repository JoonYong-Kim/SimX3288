/**
 * @fileoverview SimX Communcation Javascript API
 * @author tombraid@snu.ac.kr
 * @version 0.1.0
 * @since 2023.05.03
 */

var SimXComm = function (host) {
  var _host = host;
  var _client = mqtt.connect("ws://" + host + ":9001", 
    {clean: true, connectTimeout: 4000, clientId: 'simx'});
  
  var initialize = function () {
    _client.on('connect', function () {
      console.log('Connected');
      _client.subscribe('simx/#', function (err) {
        if (!err) {
          console.log('Subscribed');
        }
      })
    });

    _client.on('message', function (topic, message) {
      // message is Buffer
      if (topic == "simx/res") {
        console.log(topic);
        console.log(message);
      } else if (topic == "simx/reg") {
      }
      $("#test").text(message.toString());
    })
  };

  var read = function(addr, count) {
  };

  var write = function(addr, content) {
  };

  var update = function(id, list, comp) {
  };

  var parse = function(msg) {
    if (msg["addr"] == 1) {
      if (msg["ret"][0] != null) {
      } else {
      }
      if (msg["ret"][1] != null) {
      } else {
      }
    } else if (msg["addr"] == 101) {
    } else if (msg["addr"] == 201) {
    } else if (msg["addr"] == 204) {
    } else if (msg["addr"] == 401) {
    }
  };

  return {
    initialize: initialize
  };
};

//module.exports = SimXComm();

