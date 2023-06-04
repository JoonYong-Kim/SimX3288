#/bin/bash

stopall () {
  echo "stop all"
  kill -ef -9 $(head -n 1 /var/run/ns2023.pid)
  kill -ef -9 $(head -n 1 /var/run/ksmaster.pid)
}

# mode 1
startsim () {
  echo "start simulator"
  python3 ../svr/ksmaster.py start 1
  python3 ../../nutrient_supply_controller/test/ns2023.py start sim
  echo "1" > ../mode/real.mode
}

# mode 2
startctrl () {
  echo "start controller"
  python3 ../svr/ksmaster.py run 2
  echo "2" > ../mode/real.mode
}

# mode 3
startsimnctrl() {
  echo "start simulator & controller"
  python3 ../svr/ksmaster.py run 3
  python3 ../../nutrient_supply_controller/test/ns2023.py start sim
  echo "3" > ../mode/real.mode
}

# mode 4
startnut () {
  echo "start nutrient-supplier"
  python3 ../../nutrient_supply_controller/test/ns2023.py start real
  echo "4" > ../mode/real.mode
}

uimode=$(head -n 1 ../mode/ui.mode)
realmode=$(head -n 1 ../mode/real.mode)

if [ "$uimode" != "$realmode" ]; then
  stopall
  case $uimode in
    "1")
      echo "change mode to 1" $uimode
      startsim
      ;;
    "2")
      echo "change mode to 2" $uimode
      startctrl
      ;;
    "3")
      echo "change mode to 3" $uimode
      startsimnctrl
      ;;
    "4")
      echo "change mode to 4" $uimode
      startnut
      ;;
  esac
else
  echo "no need to change"
fi
