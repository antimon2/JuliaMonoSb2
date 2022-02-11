#!/bin/bash

# sudo apt update
# sudo apt -y install fontforge unar
# pip install fonttools

SOURCE=${JULIAMONO_SB2_SOURCE_FONTS_PATH:-"./sourceFonts"}
DIST="$(pwd)/dist"
mkdir -p "${DIST}"
log="${DIST}/log.txt"
touch $log

mkdir -p "${SOURCE}"
cd "${SOURCE}"

if [ ! -e "JuliaMono_wo_lg-Regular.ttf" ]; then
  echo "Prepare JuliaMono Font" | tee -a $log
  curl -LO "https://github.com/cormullion/juliamono/releases/download/v0.043/JuliaMono-ttf.tar.gz" | tee -a $log
  unar JuliaMono-ttf.tar.gz 2>&1 | tee -a $log
  for f in $(find ./JuliaMono-ttf/ -name "*.ttf" | grep -e "-Regular\.\|-RegularItalic\.\|-Bold\.\|-BoldItalic\."); do
    parts=($(IFS=-; echo $(basename "$f")))
    newf="${parts[0]}_wo_lg-${parts[1]}"
    pyftsubset "$f" '*' --output-file=./${newf} --layout-features-=calt,liga | tee -a $log
  done
  rm -rf JuliaMono-ttf
  rm JuliaMono-ttf.tar.gz
fi

if [ ! -e "mgenplus-1m-regular.ttf" ]; then
  echo "Prepare MgenPlus Font" | tee -a $log
  curl -LO "https://osdn.jp/downloads/users/8/8597/mgenplus-20150602.7z" | tee -a $log
  unar mgenplus-20150602.7z | tee -a $log
  cp mgenplus-20150602/mgenplus-1m-regular.ttf ./
  cp mgenplus-20150602/mgenplus-1m-bold.ttf ./
  rm -rf mgenplus-20150602
  rm mgenplus-20150602.7z
fi

cd ..

echo "Build" | tee -a "${log}"
fontforge -lang=py -script JuliaMono_Sb2.py 2>/dev/null | tee -a "${log}"
