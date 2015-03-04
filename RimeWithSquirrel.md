## Build Squirrel from Scratch ##

0. You should already have installed cmake, git and Xcode with Command Line Tools.

1. Install dependencies with [Homebrew](http://mxcl.github.com/homebrew/).
```
brew install boost
```

also:
```
brew install glog
brew install opencc
brew install kyoto-cabinet
brew install yaml-cpp
```

> Alternatively, you can build these libraries without installing them (except for **boost**), after checking out the code.
```
# after step 2.
cd librime
git submodule update --init
make -f Makefile.xcode thirdparty
```

2. Checkout the code.
```
git clone git@github.com:lotem/squirrel.git

# for brise & librime
cd squirrel
git submodule update --init
```

3. Build Squirrel.
```
make

# or as developer:
#make debug
```

## Test it on your Mac ##

```
sudo make install

# or as developer:
#sudo make install-debug
#killall Squirrel
```

That's it. Thanks for reading.