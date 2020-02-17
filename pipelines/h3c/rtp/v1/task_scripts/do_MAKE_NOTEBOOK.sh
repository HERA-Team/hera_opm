set -e

if [ $2 == "None" ];
then
    src_dir="$(dirname $0)"
    source ${src_dir}/_common.sh

    export DATA_PATH=`pwd`

    jd=$(get_int_jd ${1})

    export JULIANDATE=$jd

    OUTPUT=data_inspect_"$jd".ipynb
    OUTPUTDIR=$3
    BASENBDIR=$3

    jupyter nbconvert --output=$OUTPUTDIR/$OUTPUT \
    --to notebook \
    --ExecutePreprocessor.allow_errors=True \
    --ExecutePreprocessor.timeout=-1 \
    --execute $BASENBDIR/data_inspect_H3C.ipynb
fi
