> solve_size.out
> /home/thiagoepdc/experiments/nfs/pre_replay_on_server_side.all.size

for file in `ls /home/thiagoepdc/experiments/original_input/2011_10_21-*`
do
	python solve_pre_replay_fsize.py /home/thiagoepdc/experiments/nfs/pre_replay_on_server_side.all $file >> solve_size.out
done

python merge_solve_size_lines.py solve_size.out /home/thiagoepdc/experiments/nfs/pre_replay_on_server_side.all > /home/thiagoepdc/experiments/nfs/pre_replay_on_server_side.all.size
