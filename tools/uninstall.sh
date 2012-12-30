ui_common()
{
	if [ -f "$SH_CONFIG" ] || [ -h "$SH_CONFIG" ]; then
		while true; do
			HK_FOUND=$(grep -m 1 -x "$SH_HOTLINE" "$SH_CONFIG")
			if [ -z "$HK_FOUND" ]; then
				break
			fi
			# http://stackoverflow.com/questions/5295912/how-to-delete-a-line-containg-string-from-file-in-unix-or-solaris
			grep -Fxv "$HK_FOUND" "$SH_CONFIG" > "${SH_CONFIG}_tmp"
			mv "${SH_CONFIG}_tmp" "$SH_CONFIG"
		done
	else
		echo "Configuration file not found!"
		echo "You will have to remote bindings yourself :(."
		return 1
	fi

	return 0
}

ui_bash()
{
	ui_common
}

ui_zsh()
{
	ui_common
	if [ $? -ne 0 ]; then
		return 1
	fi
	UI_P[1]="shpush()"
	UI_P[2]="{"
	UI_P[3]="  TMP_OUT=\$(~/.shearch/src/shearch.py 3>&1 1>&2)"
	UI_P[4]="  print -z \$TMP_OUT"
	UI_P[5]="}"

	while true; do
		UI_R=$(grep -m 1 -Fxn "${UI_P[3]}" "$SH_CONFIG" | cut -d: -f1)
		UI_R=$((UI_R + 0)) # Avoid "unknown condition" error.

		if [ $UI_R -gt 2 ]; then
			i=1
			j=$(($UI_R - 2))
			block_match=0
			for (( i=1; i<=5; i++ )); do
				tmp_line=$(head -n $j "$SH_CONFIG" | tail -1)
				if [ "${UI_P[$i]}" != "${tmp_line}" ]; then
					break
				fi
				j=$((j + 1))
			done

			if [ $i -eq 6 ]; then
				k=$(($UI_R - 2))
				j=$((j - 1))
				sed -e "${k},${j}d" <"$SH_CONFIG" >"${SH_CONFIG}_tmp"
				mv "${SH_CONFIG}_tmp" "$SH_CONFIG"
			fi
		else
			break
		fi
	done
}

if [[ -d ~/.shearch ]]; then
	echo "Removing ~/.shearch"
	rm -rf ~/.shearch
else
	echo "Cannot find shearch's default folder."
	return 1
fi

if [ "$ZSH_VERSION" ]; then
	SH_CONFIG=~/.zshrc
	SH_HOTLINE="^bindkey -s \".*\" \" shpush\\\n\"$"
	ui_zsh
elif [ "$BASH_VERSION" ]; then
	SH_CONFIG=~/.bashrc
	SH_HOTLINE="^bind '\".*\": \"\`python ~/.shearch/src/shearch.py 3>&1 1>&2\`\\\e\\\C-e\"'$"
	ui_bash
else
	echo "You will have to remove bindings yourself :(."
fi

echo -e "\033[1;33;40m"'     _______. __         _______     ___      .______        ______  __    __ '"\033[0m"
echo -e "\033[1;33;40m"'    /       ||  |       |   ____|   /   \     |   _  \      /      ||  |  |  |'"\033[0m"
echo -e "\033[1;33;40m"'   |   (----`|  |_____  |  |__     /  ^  \    |  |_)  |    |  ,----;|  |__|  |'"\033[0m"
echo -e "\033[1;33;40m"'    \   \    |   __   | |   __|   /  /_\  \   |      /     |  |     |   __   |'"\033[0m"
echo -e "\033[1;33;40m"'.----)   |   |  |  |  | |  |____ /  _____  \  |  |\  \----.|  `----.|  |  |  |'"\033[0m"
echo -e "\033[1;33;40m"'|_______/    |__|  |__| |_______/__/     \__\ | _| `._____| \______||__|  |__|'"\033[0m"
echo -e "\033[1;33;40m"'                                                                              '"\033[0m"
echo -e "\033[0;33;40m"'                     shearch is degenerated, noxious and depraved             '"\033[0m"
echo -e "\033[0;33;40m"' and has been uninstalled.                                                    '"\033[0m"
