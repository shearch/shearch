current_path=`pwd`
if [[ -d ~/.shearch ]]; then
	cd ~/.shearch
else
	echo "${HOME}/.shearch directory does not exist."
	echo "You have to install shearch first in order to upgrade."
	return 1
fi

if git remote add upstream_tmp git://github.com/shearch/shearch.git; then
	echo -e "\033[0;32mChecking for the latest version.\033[0m"
else
	echo -e "\033[0;32mOops! Something went wrong. We'll try again later.\033[0m"
	cd "$current_path"
	return 1
fi

if git pull upstream_tmp master; then
	echo -e "\033[1;33;40m"'     _______. __         _______     ___      .______        ______  __    __ '"\033[0m"
	echo -e "\033[1;33;40m"'    /       ||  |       |   ____|   /   \     |   _  \      /      ||  |  |  |'"\033[0m"
	echo -e "\033[1;33;40m"'   |   (----`|  |_____  |  |__     /  ^  \    |  |_)  |    |  ,----;|  |__|  |'"\033[0m"
	echo -e "\033[1;33;40m"'    \   \    |   __   | |   __|   /  /_\  \   |      /     |  |     |   __   |'"\033[0m"
	echo -e "\033[1;33;40m"'.----)   |   |  |  |  | |  |____ /  _____  \  |  |\  \----.|  `----.|  |  |  |'"\033[0m"
	echo -e "\033[1;33;40m"'|_______/    |__|  |__| |_______/__/     \__\ | _| `._____| \______||__|  |__|'"\033[0m"
	echo -e "\033[1;33;40m"'                                                                              '"\033[0m"
	echo -e "\033[0;33;40m"'                     It"s not a secret when you have shearch.                 '"\033[0m"
	echo -e "\033[0;32;40m"'...has been successfully updated!                                             '"\033[0m"
else
	echo -e "\033[0;32mOops! Something went wrong. We'll try again later.\033[0m"
fi

cd "$current_path"
git remote rm upstream_tmp
