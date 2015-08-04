#!/bin/sh
#buaa
buaa2ucsd="/home/zwzhang/placement4/buaa2ucsd/placement4.log /home/idpl/results/buaa2ucsd/timeRead /home/kunq/logs_analyzer/buaa/buaa2ucsd_out.log"
buaa2cnic="/home/zwzhang/placement4/buaa2cnic/placement4.log /home/idpl/results/buaa2cnic/timeRead /home/kunq/logs_analyzer/buaa/buaa2cnic_out.log"
buaa2wisc="/home/zwzhang/placement4/buaa2wisc/placement4.log /home/idpl/results/buaa2wisc/timeRead /home/kunq/logs_analyzer/buaa/buaa2wisc_out.log"

#wisc
wisc2buaa="/home/idpl/results/wisc2buaa/placement4.log /home/idpl/results/wisc2buaa/timeRead /home/kunq/logs_analyzer/wisc/wisc2buaa_out.log"
wisc2ucsd="/home/idpl/results/wisc2ucsd/placement4.log /home/idpl/results/wisc2ucsd/timeRead /home/kunq/logs_analyzer/wisc/wisc2ucsd_out.log"
wisc2cnic="/home/idpl/results/wisc2cnic/placement4.log /home/idpl/results/wisc2cnic/timeRead /home/kunq/logs_analyzer/wisc/wisc2cnic_out.log"
wisc2calit2="/home/idpl/results/wisc2calit2/placement4.log /home/idpl/results/wisc2calit2/timeRead /home/kunq/logs_analyzer/wisc/wisc2calit2_out.log"

#ucsd
ucsd2buaa="/home/idpl/results/ucsd2buaa/placement4.log /home/idpl/results/ucsd2buaa/timeRead /home/kunq/logs_analyzer/ucsd/ucsd2buaa_out.log"
ucsd2cnic="/home/idpl/results/ucsd2cnic/placement4.log /home/idpl/results/ucsd2cnic/timeRead /home/kunq/logs_analyzer/ucsd/ucsd2cnic_out.log"
ucsd2wisc="/home/idpl/results/ucsd2wisc/placement4.log /home/idpl/results/ucsd2wisc/timeRead /home/kunq/logs_analyzer/ucsd/ucsd2wisc_out.log"
physics2calit2="/home/idpl/results/physics2calit2/placement4.log /home/idpl/results/physics2calit2/timeRead /home/kunq/logs_analyzer/physics/physics2calit2_out.log"

#calit2
calit2physics="/home/idpl/results/calit2physics/placement4.log /home/idpl/results/calit2physics/timeRead /home/kunq/logs_analyzer/calit2/calit2physics_out.log"
calit2wisc="/home/idpl/results/calit2wisc/placement4.log /home/idpl/results/calit2wisc/timeRead /home/kunq/logs_analyzer/calit2/calit2wisc_out.log"



WORKSPACE="/home/kunq/analyzer0728/"
ANALYZER_PATH="${WORKSPACE}client.py"
SHELL_PATH=${WORKSPACE}
ALL_PARAMS=(buaa2ucsd buaa2cnic buaa2wisc wisc2buaa wisc2ucsd wisc2cnic wisc2calit2 ucsd2buaa ucsd2cnic ucsd2wisc physics2calit2 calit2physics calit2wisc)

for index in ${ALL_PARAMS[@]}
do
	eval params=\$${index}
	params_arr=($params)
	${ANALYZER_PATH} -l ${params_arr[0]} -t ${params_arr[1]} -s ${SHELL_PATH} >> ${params_arr[2]} 2>&1
done
