#后端功能和实现方式
后端主要完成以下几个功能：
1）PIC相关：
1.1）解析video文件，将目标帧数据保存为pic，[yolo]；
2.2）对比两个pic是否是同一个实体[triple ResNet]；
2）DB相关：
2.1）保存video文件中提取到的pic信息，及其他信息（pic，size，platform，date，category，price）保存到DB中；
2.2）根据输入信息（size，category，pic），与DB中保存的数据比对后，给出TOP8匹配结果；
具体描述和实现方式如下所述
##PIC处理相关技术路径
为了实现对video文件的解析，在video playing的同时，使用yolo模型对每一帧数据进行判断，并将目标区域以指定格式，指定文件名格式，保存到指定的文件目录。这期间涉及到的技术实现方案包括yolo的模式识别，opencv使用，格式定义等细节实现。
###yolo相关的技术方案介绍
在使用yolo完成上述功能之前，首先需要对yolo的不同版本的特点有基本了解，信息汇总如下表所示：
####YOLO版本选择


####fine-turing

#####category定义
#####标记和存储

####使用Yolo解析video文件


###PIC比对
####模型选择（resnet+Triplet Loss）
####fine turing
####比对结果
