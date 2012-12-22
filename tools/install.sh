# This installer is a rip of oh-my-zsh's and I am ashamed. Sorry Robby.
# https://github.com/robbyrussell/oh-my-zsh

if [ -d ~/.shearch ]
then
  echo "\033[0;33mYou already have shearch installed.\033[0m You'll need to remove ~/.shearch if you want to install"
  exit
fi

echo "\033[0;34mCloning shearch...\033[0m"
hash git >/dev/null && /usr/bin/env git clone https://github.com/agiz/shearch.git ~/.shearch || {
  echo "git not installed"
  exit
}

echo "\033[0;34mLooking for an existing zsh config...\033[0m"
#if [ -f ~/.zshrc ] || [ -h ~/.zshrc ]
#then
#  echo "\033[0;33mFound ~/.zshrc.\033[0m \033[0;32mBacking up to ~/.zshrc.pre-oh-my-zsh\033[0m";
#  mv ~/.zshrc ~/.zshrc.pre-oh-my-zsh;
#fi

#echo "\033[0;34mUsing the Oh My Zsh template file and adding it to ~/.zshrc\033[0m"
#cp ~/.oh-my-zsh/templates/zshrc.zsh-template ~/.zshrc

#echo "\033[0;34mCopying your current PATH and adding it to the end of ~/.zshrc for you.\033[0m"
#echo "export PATH=$PATH" >> ~/.zshrc

# http://patorjk.com/software/taag/#p=display&f=Slant&t=oh%20my%20zsh
# http://patorjk.com/software/taag/#p=display&f=Star%20Wars&t=shearch
echo "\033[0;32m"'      _______. __         _______     ___      .______        ______  __    __  '"\033[0m"
echo "\033[0;32m"'     /       ||  |       |   ____|   /   \     |   _  \      /      ||  |  |  | '"\033[0m"
echo "\033[0;32m"'    |   (----`|  |_____  |  |__     /  ^  \    |  |_)  |    |  ,----;|  |__|  | '"\033[0m"
echo "\033[0;32m"'     \   \    |   __   | |   __|   /  /_\  \   |      /     |  |     |   __   | '"\033[0m"
echo "\033[0;32m"' .----)   |   |  |  |  | |  |____ /  _____  \  |  |\  \----.|  `----.|  |  |  | '"\033[0m"
echo "\033[0;32m"' |_______/    |__|  |__| |_______/__/     \__\ | _| `._____| \______||__|  |__| '"\033[0m"
echo ""
# http://www.sloganmaker.com/
echo "\033[0;32m"'                     It"s not a secret when you have shearch.                   '"\033[0m"
# shearch is degenerated, noxious and depraved. # Hate Sloganmaker
echo "\n \033[0;32m....is now installed.\033[0m"

#/usr/bin/env zsh
#source ~/.zshrc