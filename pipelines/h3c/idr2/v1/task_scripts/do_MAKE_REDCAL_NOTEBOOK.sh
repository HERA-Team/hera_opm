set -e

src_dir="$(dirname $0)"
source ${src_dir}/_common.sh

jd=$(get_int_jd ${1})
OUTPUT=Redcal_Inspect_"$jd".ipynb
BASENBDIR=$2

export DATA_PATH=`pwd`
export JULIANDATE=$jd

jupyter nbconvert --output=$OUTPUT \
--to notebook \
--ExecutePreprocessor.allow_errors=True \
--ExecutePreprocessor.timeout=-1 \
--execute ${BASENBDIR}/Redcal_Inspect_H3C.ipynb

# git pull origin master
# git add ${OUTPUT}
# git commit -m "RTP data inspection notebook commit for JD ${jd}"
# git push origin master
