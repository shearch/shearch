if [ -d ~/.shearch ]
then
	echo "\033[0;31mYou already have shearch installed.\033[0m You'll need to remove ~/.shearch if you want to reinstall it."
	return 1
fi

echo "\033[0;32mCloning shearch...\033[0m"
hash git >/dev/null && /usr/bin/env git clone https://github.com/shearch/shearch.git ~/.shearch || {
	echo "git not installed"
	return 1
}

response=1
# If this stays 1, then we were unable to bind key.

f_keys()
{
	FKEY[$((SH_J))]="\e[OP~"
	FKEY[$((SH_J + 1))]="\e[OQ~"
	FKEY[$((SH_J + 2))]="\e[OR~"
	FKEY[$((SH_J + 3))]="\e[OS~"
	FKEY[$((SH_J + 4))]="\e[15~"
	FKEY[$((SH_J + 5))]="\e[17~"
	FKEY[$((SH_J + 6))]="\e[18~"
	FKEY[$((SH_J + 7))]="\e[19~"
	FKEY[$((SH_J + 8))]="\e[20~"
	FKEY[$((SH_J + 9))]="\e[21~"
	FKEY[$((SH_J + 10))]="\e[23~"
	FKEY[$((SH_J + 11))]="\e[24~"
	FKEY[$((SH_J + 12))]="-1"
}

sf_keys()
{
	FKEY[$((SH_J))]="\e[1;2P~"
	FKEY[$((SH_J + 1))]="\e[1;2Q~"
	FKEY[$((SH_J + 2))]="\e[1;2R~"
	FKEY[$((SH_J + 3))]="\e[1;2S~"
	FKEY[$((SH_J + 4))]="\e[15;2~"
	FKEY[$((SH_J + 5))]="\e[17;2~"
	FKEY[$((SH_J + 6))]="\e[18;2~"
	FKEY[$((SH_J + 7))]="\e[19;2~"
	FKEY[$((SH_J + 8))]="\e[20;2~"
	FKEY[$((SH_J + 9))]="\e[21;2~"
	FKEY[$((SH_J + 10))]="\e[23;2~"
	FKEY[$((SH_J + 11))]="\e[24;2~"
	FKEY[$((SH_J + 12))]="-1"
}

bash_key_get()
{
	total=${#FKEY[*]}
	total=$((total + SH_J))
	for (( i=$SH_J; i<$(( $total )); i++ ))
	do
		if [ "$SH_HOTKEY" = ${FKEY[$i]} ]; then
			return $((i + SH_O))
		fi
	done

	return -1
}

parse_key()
{
	f_keys
	bash_key_get
	res=$?
	if [ $res -ge 1 ] && [ $res -le 12 ]; then
		echo "F${res}"
		return 0
	fi

	sf_keys
	bash_key_get
	res=$?
	if [ $res -ge 1 ] && [ $res -le 12 ]; then
		echo "Shift + F${res}"
		return 0
	fi

	echo ""
	echo "Installer can map only 'F' keys and Shitf + 'F' keys at the moment."
	return 1
}

map_key()
{
	# Read user key from installer's argument.
	echo -ne "\033[0;32mBindkey: \033[0m"
	if [ "${SH_HOTKEY:0:1}" = "F" ]; then
		f_keys
		f_off=$((${SH_HOTKEY:1} - $SH_O))

		if [ $f_off -ge $SH_S ] && [ $f_off -le $SH_E ]; then
			SH_HOTKEY=${FKEY[$f_off]}
			printf "F%s\n" $(($f_off + $SH_O))
			return 0
		else
			echo "Selected key is out of range."
		fi
	elif [ "${SH_HOTKEY:0:1}" = "S" ]; then
		sf_keys
		f_off=$((${SH_HOTKEY:2} - $SH_O))
		if [ $f_off -ge $SH_S ] && [ $f_off -le $SH_E ]; then
			SH_HOTKEY=${FKEY[$f_off]}
			printf "Shift + F%s\n" $(($f_off + $SH_O))
			return 0
		else
			echo "Selected key is out of range."
		fi
	else
		echo "Installer can map only 'F' keys and Shift + 'F' keys at the moment."
	fi

	return 1
}

read_key()
{
	# Read user key from stdin.
	echo -ne "\033[0;32mEnter your hotkey and press <RETURN>: \033[0m"
	# http://ss64.com/bash/read.html
	read -s SH_HOTKEY
	if [ -z "$SH_HOTKEY" ]; then
		echo ""
		echo "You did not enter vaild key, defaulting to F12."
		SH_HOTKEY="\e[24~"
		return 0
	elif [ ${SH_HOTKEY:0:1} = "" ]; then
		SH_HOTKEY="\e${SH_HOTKEY:1}"
	fi

	parse_key
	return $?
}

sh_common()
{
	echo $SH_NAME

	echo -ne "\033[0;32mChecking for configuration file... \033[0m"
	if [ -f "$SH_CONFIG" ] || [ -h "$SH_CONFIG" ]; then
		echo "$SH_CONFIG"
	else
		echo "not found!"
		echo -e "\033[0;32mCreating new configuration file.\033[0m"
		touch "$SH_CONFIG"
	fi

	HK_FOUND=$(grep -m 1 -x "$SH_HOTLINE" "$SH_CONFIG")
}

hk_bash()
{
	sh_common

	if [ -n "$HK_FOUND" ]; then
		[[ $HK_FOUND =~ $SH_REGEX ]]
		name="${BASH_REMATCH[1]}"
		echo -ne "\033[0;31mYou already have key of shearch bound to... \033[0m"
		SH_HOTKEY="${name}"
		parse_key
		if [ $? -eq 1 ]; then
			echo "You might have already set your but we cannot tell which one :(."
		fi
		return 2
	else
		SH_J=0 # Index of first element in an array.
		SH_O=1 # Offset for F keys.
		SH_S=0 # Start position of F keys
		SH_E=11 # End position of F keys
		if [ -n "$SH_HOTKEY" ]; then
			map_key
			response=$?
		else
			read_key
			response=$?
		fi
	fi

	if [ $response -eq 0 ]; then
		shortcut="bind '\"${SH_HOTKEY}\": \"\`python ~/.shearch/src/shearch.py 3>&1 1>&2\`\\e\\C-e\"'"
		printf "\n%s\n" "$shortcut" >> "$SH_CONFIG"
		return 0
	fi

	return 1
}

hk_zsh()
{
	sh_common

	if [ -n "$HK_FOUND" ]; then
		[[ $HK_FOUND =~ $SH_REGEX ]]
		name="${match[1]}"
		echo -ne "\033[0;31mYou already have key of shearch bound to... \033[0m"
		SH_HOTKEY="${name}"
		parse_key
		if [ $? -eq 1 ]; then
			echo "You might have already set your but we cannot tell which one :(."
		fi
		return 2
	else
		typeset -A keymap
		SH_J=1 # Index of first element in an array.
		SH_O=0 # Offset for F keys.
		SH_S=1 # Start position of F keys
		SH_E=12 # End position of F keys
		if [ -n "$SH_HOTKEY" ]; then
			map_key
			response=$?
		else
			read_key
			response=$?
		fi
	fi

	if [ $response -eq 0 ]; then
		echo "shpush()\n{\n  TMP_OUT=\$(~/.shearch/src/shearch.py 3>&1 1>&2)\n  print -z \$TMP_OUT\n}" >> "$SH_CONFIG"

		shortcut="bindkey -s \"${SH_HOTKEY}\" \" shpush\\n\""
		printf "\n%s\n" "$shortcut" >> "$SH_CONFIG"
		return 0
	fi

	return 1
}

if [ -z "$1" ]; then
	SH_HOTKEY=""
else
	SH_HOTKEY="$(echo ${1} | tr '[:lower:]' '[:upper:]')"
fi

echo -ne "\033[0;32mDetecthing shell... \033[0m"
if [ "$ZSH_VERSION" ]; then
	SH_NAME="zsh"
	SH_VERSION="$ZSH_VERSION"
	SH_CONFIG=~/.zshrc
	SH_HOTLINE="^bindkey -s \".*\" \" shpush\\\n\"$"
	SH_REGEX="^bindkey -s \"(.*)\" \" shpush\\\n\"$"
	hk_zsh
	response=$?
elif [ "$BASH_VERSION" ]; then
	SH_NAME="bash"
	SH_VERSION="$BASH_VERSION"
	SH_CONFIG=~/.bashrc
	SH_HOTLINE="^bind '\".*\": \"\`python ~/.shearch/src/shearch.py 3>&1 1>&2\`\\\e\\\C-e\"'$"
	SH_REGEX="^bind '\"(.*)\": \"\`python ~/.shearch/src/shearch.py 3>&1 1>&2\`\\\e\\\C-e\"'$"
	hk_bash
	response=$?
else
	SH_NAME="other"
	SH_VERSION="-1"
	SH_CONFIG=""
	echo $SH_NAME
	echo "Unable to bound key shortcut. You will have to do it manually or use shearch without shortcut."
fi

if [ $response -eq 2 ]; then
	return 1
fi

# http://patorjk.com/software/taag/#p=display&f=Star%20Wars&t=shearch
echo -e "\033[1;33;40m"'     _______. __         _______     ___      .______        ______  __    __ '"\033[0m"
echo -e "\033[1;33;40m"'    /       ||  |       |   ____|   /   \     |   _  \      /      ||  |  |  |'"\033[0m"
echo -e "\033[1;33;40m"'   |   (----`|  |_____  |  |__     /  ^  \    |  |_)  |    |  ,----;|  |__|  |'"\033[0m"
echo -e "\033[1;33;40m"'    \   \    |   __   | |   __|   /  /_\  \   |      /     |  |     |   __   |'"\033[0m"
echo -e "\033[1;33;40m"'.----)   |   |  |  |  | |  |____ /  _____  \  |  |\  \----.|  `----.|  |  |  |'"\033[0m"
echo -e "\033[1;33;40m"'|_______/    |__|  |__| |_______/__/     \__\ | _| `._____| \______||__|  |__|'"\033[0m"
echo -e "\033[1;33;40m"'                                                                              '"\033[0m"
# http://www.sloganmaker.com/
echo -e "\033[0;33;40m"'                     It"s not a secret when you have shearch.                 '"\033[0m"
# shearch is degenerated, noxious and depraved. # Hate Sloganmaker
echo -e "\033[0;33;40m"'...is now installed.                                                          '"\033[0m"

if [ $response -eq 1 ]; then
	echo -e "\033[0;31mshearch has been installed successfully but we were unable to bind your key\033[0m"
fi

. "$SH_CONFIG"
