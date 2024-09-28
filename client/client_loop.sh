win=0
lose=0
draw=0
my_piece=0
opponent_piece=0
for i in {1..100}; do
    output=$(python main.py $1)
    line_num=0
    while IFS= read -r line; do
        line_num=$((line_num+1))
        # line 1 is the result of the game
        if [ "$line" == "win" ]; then
            win=$((win+1))
        elif [ "$line" == "lose" ]; then
            lose=$((lose+1))
        elif [ "$line" == "draw" ]; then
            draw=$((draw+1))
        fi
        # line 2 is number of My Piece
        if [ $line_num -eq 2 ]; then
            my_piece=$((my_piece+$(echo $line | sed 's/[^0-9]*//g')))
        fi
        # line 3 is number of Opponent Piece
        if [ $line_num -eq 3 ]; then
            opponent_piece=$((opponent_piece+$(echo $line | sed 's/[^0-9]*//g')))
        fi
    done <<< "$output"

    if [ $? -ne 0 ]; then
        echo "Error in iteration" $i
        break
    fi
    echo $i "th iteration"
    sleep 0.05
done

echo "Win: " $win
echo "Loss: " $lose
echo "Draw: " $draw
echo "My Piece: " $my_piece
echo "Opponent Piece: " $opponent_piece
