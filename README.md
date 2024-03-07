《纯阳别册》
------------------------------------------

- "纯阳"在道教中通常指的是一种纯净无杂的阳性原则，也是道教历史上著名的人物吕洞宾的尊号，他被认为是达到了道教修炼的最高境界——纯阳无极。"别册"则通常指的是附录、补遗或是特别编制的册子，有时候也指独立出版的特殊书籍或文集。

- 将`《纯阳别册》`翻译成英文时，可以根据上下文的不同有不同的方式。如果是作为道教文化或修炼方法的讨论，可以翻译为 `"The Annex of Pure Yang"`或 `"The Supplement of Pure Yang"`，强调其作为补充材料或特别辑的性质。如果是强调书中内容或特定的修炼方法，也可以翻译为 `"The Pure Yang Manual"` 或 `"The Pure Yang Compendium"`，更侧重于其作为一本指导书或汇编的角色。

- 在这里我想强调汇编的含义。

《SRA2Fastq.wdl》
------------------------------------------
随着项目的进展，现在我有了站在更大的舞台的机会。我需要准备一个面向巨量数据的自动化的工具，我需要在WDL（Workflow Description Language，是Broad Institute专门开发用来跑流程的语言）下工作。先期目标是将文件的基本处理放在云平台。

WDL基本元件有5个，分别是定义总流程的`workflow`、定义单个任务的`task`、运行任务的`call`、定义任务中命令的`command`以及输出`output`。
![图片](https://github.com/OOAAHH/The_Pure_Yang_Compendium/assets/19518905/9ac9c4ad-78c9-4986-ab28-c7ec59b21910)

《SAM2Fastq》
------------------------------------------
实在是缺少必要的工具实现我这样特殊的需求，无奈自己写一个。优化空间蛮大的。
<img width="1178" alt="截屏2024-03-06 23 35 54" src="https://github.com/OOAAHH/The_Pure_Yang_Compendium/assets/19518905/b420dbba-7266-40cb-ac76-bc2391579fcc">

结果还行，就是python慢了些。
![图片](https://github.com/OOAAHH/The_Pure_Yang_Compendium/assets/19518905/5a2ee751-1d90-4c2f-b592-8cc508b5ba40)

虽然RG改变的原因不明确，但是至少符合预期。

<img width="657" alt="截屏2024-03-07 13 29 00" src="https://github.com/OOAAHH/The_Pure_Yang_Compendium/assets/19518905/366c5ef6-617e-46a9-9f3e-ad3155ca365c">
