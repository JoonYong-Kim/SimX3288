#/bin/bash

HOME=/home/debian
SIMX=$HOME/SimX3288
NUT=$SIMX/nutrient_supply_controller

stopall () {
  echo "stop all"
  kill -9 $(head -n 1 /var/run/ns2023.pid)
  kill -9 $(head -n 1 /var/run/ksmaster.pid)
}

# mode 1
startsim () {
  echo "start simulator"
  cd $SIMX/svr; python3 ksmaster.py start 1
  cd $NUT/test; python3 ns2023.py start sim
  echo "1" > $SIMX/mode/real.mode
}

# mode 2
startctrl () {
  echo "start controller"
  cd $SIMX/svr; python3 ksmaster.py start 2
  echo "2" > $SIMX/mode/real.mode
}

# mode 3
startsimnctrl() {
  echo "start simulator & controller"
  cd $SIMX/svr; python3 ksmaster.py start 3
  cd $NUT/test; python3 ns2023.py start sim
  echo "3" > $SIMX/mode/real.mode
}

# mode 4
startnut () {
  echo "start nutrient-supplier"
  cd $NUT/test; python3 ns2023.py start real
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
fi
