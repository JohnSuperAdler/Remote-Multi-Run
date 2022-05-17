# $1: number of script to be executed
# $2: python script file / bash script

##### $1 number of run

if [ $1 ]; then
    run_pane=$1
else
    run_pane=3
fi
run_win=$(( run_pane / 4 + 1 ))
run_mod=$(( run_pane % 4 ))
echo "[+] Script brancher:"
echo "    [-] Number of run: $run_pane"
echo "    [-] Window needed: $run_win"

##### $2 command

tmux new-session -d -s 'socket_plug'
tmux switch -t 'socket_plug'
tmux new-window
tmux send-keys 'htop' C-m
tmux split-window -v
tmux send-keys "watch sensors" C-m
tmux split-window -h 
tmux send-keys "watch nvidia-smi" C-m

for ((i=1; i <= $run_win ; i++)); do
    tmux new-window
    tmux split-window -h
    tmux split-window -v
    tmux select-pane -t 0
    tmux split-window -v
    if [ $i = $run_win ]
    then
        for ((j=0 ; j <= $run_mod - 1 ; j++ )); do
            tmux select-pane -t $j
            tmux send-keys "$2" C-m
        done
    else
        for ((j=0 ; j <= 3 ; j++ )); do
            tmux select-pane -t $j
            tmux send-keys "$2" C-m
        done
    fi
done