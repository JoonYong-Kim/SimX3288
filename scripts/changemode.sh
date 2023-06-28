#/bin/bash

HOME=/home/debian
SIMX=$HOME/SimX3288
NUT=$SIMX/nutrient_supply_controller

stopall () {
  echo "stop all"
  pkill -ef -9 ns2023
  pkill -ef -9 ksmaster
  sleep 1
}

checkns2023 () {
  service ns2023 status
  if [ $? != "0" ]; then
    service ns2023 start
  fi
}

checkksmaster () {
  service ksmaster status
  if [ $? != "0" ]; then
    service ksmaster start
  fi
}

# mode 1
startsim () {
  echo "start simulator"
  service ns2023 start
  sleep 1
  service ksmaster start
  echo "1" > $SIMX/mode/real.mode
}

# mode 2
startctrl () {
  echo "start controller"
  service ksmaster start
  echo "2" > $SIMX/mode/real.mode
}

# mode 3
startsimnctrl() {
  echo "start simulator & controller"
  service ns2023 start
  sleep 1
  service ksmaster start
  echo "3" > $SIMX/mode/real.mode
}

# mode 4
startnut () {
  echo "start nutrient-supplier"
  service ns2023 start
  echo "4" > $SIMX/mode/real.mode
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
  case $realmode in
    "1")
      checkns2023
      checkksmaster
      ;;
    "2")
      checkksmaster
      ;;
    "3")
      checkns2023
      checkksmaster
      ;;
    "4")
      checkns2023
      ;;
  esac
fi
