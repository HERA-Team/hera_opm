set -e

if [ $2 == "None" ];
then
    src_dir="$(dirname $0)"
    source ${src_dir}/_common.sh

    export DATA_PATH=`pwd`

    jd=$(get_int_jd ${1})

    export JULIANDATE=$jd

    OUTPUT=Redcal_Inspect_"$jd".ipynb
    BASENBDIR=$3

    cd ${BASENBDIR}

    jupyter nbconvert --output=$OUTPUT \
    --to notebook \
    --ExecutePreprocessor.allow_errors=True \
    --ExecutePreprocessor.timeout=-1 \
    --execute Redcal_Inspect_H3C.ipynb

    git pull origin master
    git add ${OUTPUT}
    git commit -m "RTP redcal notebook commit for JD ${jd}"
    git push origin master

    cd ${src_dir}
fi
