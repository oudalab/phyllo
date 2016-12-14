#!/bin/bash
#export JQLITE="$HOME/bin/jqlite"
export JQLITE="/usr/local/bin/jqlite"
mkdir -p $JQLITE
cd $JQLITE
curl -o sqlite.tar.gz https://www.sqlite.org/src/tarball/sqlite.tar.gz
tar xvzf sqlite.tar.gz
mkdir bld
cd bld

export CFLAGS="-DSQLITE_ENABLE_COLUMN_METADATA \
-DSQLITE_ENABLE_DBSTAT_VTAB \
-DSQLITE_ENABLE_FTS3 \
-DSQLITE_ENABLE_FTS4 \
-DSQLITE_ENABLE_FTS5 \
-DSQLITE_ENABLE_JSON1 \
-DSQLITE_ENABLE_STAT4 \
-DSQLITE_ENABLE_UPDATE_DELETE_LIMIT \
-DSQLITE_SECURE_DELETE \
-DSQLITE_SOUNDEX \
-DSQLITE_ENABLE_FTS3_TOKENIZER \
-DSQLITE_TEMP_STORE=3 \
-DSQLITE_ENABLE_FTS3_PARENTHESIS \
-O2 \
-fPIC"
LIBS="-lm" ../sqlite/configure --prefix=$JQLITE --enable-static --enable-shared
make
make install

cd $JQLITE
git clone https://github.com/rogerbinns/apsw
cd apsw
cp $JQLITE/bld/sqlite3ext.h .
cp $JQLITE/bld/sqlite3.h .
cp $JQLITE/bld/sqlite3.c .
echo -e "library_dirs=$JQLITE/lib" >> setup.cfg
echo -e "include_dirs=$JQLITE/include" >> setup.cfg
LIBS="-lm" python3 setup.py build --enable-all-extensions

cd $JQLITE/apsw
python3 setup.py install
