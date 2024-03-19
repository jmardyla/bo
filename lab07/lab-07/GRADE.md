Dear Student,

I'm happy to announce that you've managed to get **8** out of 11 points for this assignment.
<details><summary>You have already managed to pass 7 tests, so that is encouraging!</summary>&emsp;☑&nbsp;[1p]&nbsp;Knapsack&nbsp;model&nbsp;for&nbsp;linear&nbsp;relaxation&nbsp;should&nbsp;be&nbsp;correct<br>&emsp;☑&nbsp;[1p]&nbsp;Knapsack&nbsp;model&nbsp;for&nbsp;implicit&nbsp;enum&nbsp;should&nbsp;be&nbsp;correct<br>&emsp;☑&nbsp;[2p]&nbsp;Implicit&nbsp;enumeration&nbsp;should&nbsp;correctly&nbsp;perform&nbsp;branch&nbsp;and&nbsp;bound<br>&emsp;☑&nbsp;[1p]&nbsp;Solver&nbsp;should&nbsp;find&nbsp;the&nbsp;best&nbsp;possible&nbsp;assignment<br>&emsp;☑&nbsp;[1p]&nbsp;Solver&nbsp;should&nbsp;determine&nbsp;if&nbsp;partial&nbsp;assignment&nbsp;is&nbsp;satisfiable<br>&emsp;☑&nbsp;[1p]&nbsp;Solver&nbsp;should&nbsp;find&nbsp;variable&nbsp;with&nbsp;least&nbsp;infeasibility<br>&emsp;☑&nbsp;[1p]&nbsp;Solver&nbsp;should&nbsp;assess&nbsp;total&nbsp;infeasibility&nbsp;of&nbsp;assignment</details>

There still exist some issues that should be addressed before the deadline: **2023-07-05 07:59:00 CEST (+0200)**. For further details, please refer to the following list:

<details><summary>[1p] Solver should always find first variable with non integer value from solution &gt;&gt; failed to found the first variable with float value: (problem: `ks_lecture_dp_1`):</summary>-&nbsp;got:&nbsp;None<br>-&nbsp;expected:&nbsp;x1(v:6,&nbsp;w:5)<br>-&nbsp;for&nbsp;solution:<br>&nbsp;&nbsp;&nbsp;&nbsp;-&nbsp;objective&nbsp;value:&nbsp;11.6<br>&nbsp;&nbsp;&nbsp;&nbsp;-&nbsp;assignment:<br>&nbsp;&nbsp;&nbsp;&nbsp;&emsp;-&nbsp;x0(v:5,&nbsp;w:4)&nbsp;=&nbsp;1.000<br>&nbsp;&nbsp;&nbsp;&nbsp;&emsp;-&nbsp;x1(v:6,&nbsp;w:5)&nbsp;=&nbsp;0.600<br>&nbsp;&nbsp;&nbsp;&nbsp;&emsp;-&nbsp;x2(v:3,&nbsp;w:2)&nbsp;=&nbsp;1.000</details>
<details><summary>[2p] Linear relaxation should correctly perform branch and bound &gt;&gt; Tested code raises NotImplementedError in linear_relaxation.py:40</summary></details>

-----------
I remain your faithful servant\
_Bobot_