
#author: yinxue.liu@bristol.ac.uk
#2021/01/19
#This script can be used to construct the Random Forest model in a single city mode (70% sample train, 30% sample test).
#input requires the 13 regression layers, MERIT DEM and LIDAR DTM.
#output includes the evalution of predicted error vs actual error (of MERIT), statistics of the RMSE result,
#importance score of each factor, and the MERIT DEM with predicted error subtracted.

#* The offset should be set as 0.0 if the DTM has been converted to EGM96 vertical reference system.
library(tiff)
library(raster)
library(ini)
library(Metrics)
library(ggplot2)
library(gridExtra)
library(rlist)
library(ramify)
#Load Library Random Forest
library(randomForest)
library(miscTools)
#library(lme4)
#library(nlme) 
#library(caret)
library(fields)
library(formattable)
#library(graphics)
#library(cowplot)
# Read raster as train data
#write a function for read in data
varname <- 'NTL'
factorname <- c(varname,'POP','BD','BH','SL','N1','N2','N3','N4','ELE','N5','N6','N7','N8')
targetname <- c('diff','MERIT','lidar')
coorname <- c('x','y')
readfactor<- function(factorname){
  rasterx <- raster(factorname)
  matrixx <- as.matrix(rasterx)
  row <- nrow(matrixx)
  col <- ncol(matrixx)
  size <-row*col
  listx <- resize(matrixx,size,1)
}
####################################################
#read data in first city
########################
readcity <- function(cityname,offset){
  #read data to predict error
  path <-paste0('path of regression datasets',cityname,'/RF_layers/') #path of regression factor layers
  path2 <- paste0('path of regression datasets',cityname,'/DEMs/') #path of dem layers
  #read file with tif ending to list
  factor <- list.files(path = path,pattern = '\\.tif$',full.names = TRUE)
  dem <- list.files(path=path2,pattern = '\\.tif$',full.names = TRUE)
  bd <- readfactor(factor[1])
  bh <- readfactor(factor[2])
  var <-readfactor(factor[3])
  pop<-readfactor(factor[4])
  sl <- readfactor(factor[5])

  lidar <- readfactor(dem[1])
  merit <- readfactor(dem[2])
  wam <- readfactor(dem[5])
  diff <- merit-(lidar-offset)
  #read in neighbour data
  neighb_name <- paste0(path,cityname,' city_NeighbFile.csv')
  neighb <- read.csv(neighb_name, row.names=1)
  maneighb <- (!is.na(neighb[,1:9])&(neighb[,1:9]> -1000))
  ma_n <- list()
  for (i in 1:nrow(maneighb)){
    ma_n<-append(ma_n,all(maneighb[i,1:9]))
  }
  ma <- (!is.na(var)&!is.na(pop)&!is.na(bd)&(bd>0)&!is.na(bh)&(bh>0)&!is.na(sl)&sl<10
         &!is.na(merit)&!is.na(lidar)&lidar>0&!is.na(wam))
  ma_f <- ma&unlist(ma_n)
  #get xy coordinate and add that to the dataframe
  MERITname <- dem[2]
  MERITra <- raster(MERITname)
  coor <- c()
  for (cell in (1: length(MERITra))){
    coor <- rbind(coor,xyFromCell(MERITra,cell))
  }
  ds<- data.frame(var[ma_f],pop[ma_f],bd[ma_f],bh[ma_f],sl[ma_f],neighb[ma_f,1:9],
                    diff[ma_f],merit[ma_f],lidar[ma_f]-offset,coor[ma_f,1:2])
  colnames(ds) <- c(factorname,targetname,coorname)
  return(list(ds,ma_f,merit)) 
}
city1 <- 'Manchester'
city2 <- 'Bristol'
city3 <- 'London'
city4 <- 'Beijing'
city5 <- 'Berlin'
city6 <- 'Cambridge'
city7 <- 'Carlisle'


# city7 <- 'Carlisle_boun'
# pathre <-paste0('/home/qo18712/RF_server/RF_result_NTL_multi/'
#                ,paste(city4,city5,city3,city1,city2,city6,sep=' '),'/')
list1 <- readcity(city1,0.8)
ds1 <- data.frame(list1[1])
ma_f1 <- unlist(list1[2])
merit1 <- unlist(list1[3])

list2 <- readcity(city2,0.8)
ds2 <- data.frame(list2[1])
ma_f2 <- unlist(list2[2])
merit2 <- unlist(list2[3])

list3 <- readcity(city3,0.8)
ds3 <- data.frame(list3[1])
ma_f3 <- unlist(list3[2])
merit3 <- unlist(list3[3])

list4 <- readcity(city4,-0.21)
ds4 <- data.frame(list4[1])
ma_f4 <- unlist(list4[2])
merit4 <- unlist(list4[3])

list5 <- readcity(city5,0.0)
ds5 <- data.frame(list5[1])
ma_f5 <- unlist(list5[2])
merit5 <- unlist(list5[3])

list6 <- readcity(city6,0.8)
ds6 <- data.frame(list6[1])
ma_f6 <- unlist(list6[2])
merit6 <- unlist(list6[3])

list7 <- readcity(city7,0.8)
ds7 <- data.frame(list7[1])
ma_f7 <- unlist(list7[2])
merit7 <- unlist(list7[3])
#save data as .RData
save.image(file='7city_Berlin city_non forest.RData')
#######################################
############################################################
#pack the last city estimation as a function
regression <- function(city,traincity,pathre,ds,ma_f,merit,nudge){
  set.seed(1)
  #use the same train data to predict the third city
  ind <- sample(2,nrow(ds),replace=TRUE,prob=c(0.7,0.3))
  traindata <- ds[ind==1,c(1:15)]
  #traindata <- traindata[traindata$diff>0,1:15]
  testdata <- ds[ind==2,c(1:15)]#######################################################
  testdatatarget <- ds[ind==2,16:17]################################################
  testdataxy <- ds[ind==2,18:19]####################################################
  rf <- randomForest(diff~.,data=traindata,mtry=5,ntree=500,proximity=TRUE)
  plot(rf)
  print(which.min(rf$mse))
  print(sqrt(rf$mse[which.min(rf$mse)]))
  #before plotting set all plot title to be centered
  theme_update(plot.title = element_text(hjust = 0.5))
  #calculate importance of predictors, and then plot
  importance <- importance(x=rf)
  factors <- factorname[c(1:14)]
  factors <- toupper(factors)
  dfim <- cbind(importance,'Factors'=factors,'Importance'=importance[,1]/sum(importance[,1]))
  dfim <- data.frame(dfim)
  #convert factor to numeric and then to percent
  dfim$Importance <- as.numeric(as.character(dfim$Importance))
  #as the folder of Carlisle is different from other cities
  if (city == "Carlisle_boun"){
    titlename = "Carlisle"
  }else {titlename = city}
  p <- ggplot(data=dfim, aes(x=reorder(Factors,Importance),y=Importance)) +
    geom_bar(position=position_dodge(width=0.1),stat="identity",color='blue',fill='blue',width=0.5) + 
    ggtitle(titlename)+
    #ggtitle('Carlisle') +#################
  geom_text(aes(label=percent(dfim$Importance,digits = 0)),nudge_y=nudge,size=3.0)+
    coord_flip(ylim=c(0.0,0.35))+
    scale_y_continuous(labels = function(y) paste0(y*100, "%"))
  p <- p + xlab('Factors')+ theme(plot.title=element_text(size=12),
                                  plot.subtitle=element_text(hjust=0.5,size=7))
  ggsave(filename=paste0(pathre,paste0(traincity,'-',city,'_',varname,'_worldpop_Factor Importance_35.png')),
         width=3,height=2.5)######################################################################
  # #predict with test data
  pred <- predict(rf, testdata)
  #r2 and MSE calculation
  r2 <- 1 - (sum((testdata$diff-pred)^2)/sum((testdata$diff-mean(testdata$diff))^2))
  mse <- mean((testdata$diff - pred)^2)#mean squared error
  print(paste0('r2 is ',r2))
  #Build scatterplot of test data in four cities
  data=data.frame(actual=testdata$diff, pred=pred)
  xylim <- c(min(data$actual),min(data$pred),max(data$actual),max(data$pred))
  anno <- paste('~R^2 ==~',format(round(r2, 2), nsmall = 2))
  p <- ggplot(data,aes(x=actual, y=pred))
  p<- p + geom_point(size=0.5) +
    geom_abline(mapping=aes(intercept = 0, slope = 1,color='red'),linetype='dotted',size=1) +
    ggtitle(titlename)########################################################################
  # p<- p + geom_point(size=0.5) +
  #   geom_abline(mapping=aes(intercept = 0, slope = 1,color='red'),linetype='dotted',size=1) +
  #   ggtitle('Carlisle')
  lmin <- -10
  lmax <- 40
  rx <- 0.4*(lmax-lmin)
  ry <- 0.6*(lmax-lmin)
  p <- p + scale_y_continuous(breaks=seq(lmin, lmax, 5), limits=c(lmin, lmax))+scale_x_continuous(breaks=seq(lmin, lmax, 5), limits=c(lmin, lmax))+coord_equal()
  p <- p + annotate(geom="text", x= rx,y=ry,label=anno,parse=T,size=3.5)
  p<-p+ylab('Predicted error(m)')+xlab('Actual error(m)')
  p<- p + theme(panel.border = element_blank(),
                axis.line.x = element_line(size = 0.5, linetype = "solid"),
                axis.line.y = element_line(size = 0.5, linetype = "solid"))
  p <- p + theme(plot.title = element_text(hjust = 0.5))
  p <- p + scale_color_identity(name='',labels=c("Perfect Fit"), guide="legend")
  p <- p + theme(legend.position=c(0.3,0.95),legend.text=element_text(size=10),
                 plot.title=element_text(size=12))
  print(p)
  ggsave(paste0(pathre,paste0(traincity,'-',city,'_RF_',varname,'_worldpop.png')),width=3,height=3)
  ################################################
  #remove outliers
  #select outlier dataset
  indexout <- which((testdata[,15]-pred)>5,arr.ind=TRUE)
  outlier <- cbind(testdataxy[indexout,1:2],testdata[indexout,1:15], testdatatarget[indexout,1:2],pred[indexout])
  colnames(outlier) <- c(coorname,factors,targetname,'pred')
  write.csv(outlier,file=paste0(pathre,paste0(traincity,'-',city,'_RF_',varname,'_worldpop_outlier_under5.csv')))
  ###############################################save test data into csv
  testdataADD <- cbind(testdataxy[,1:2],testdata[,1:15],testdatatarget[,1:2],pred)
  colnames(testdataADD) <- c(coorname,factors,targetname,'pred')
  write.csv(testdataADD,file=paste0(pathre,paste0(traincity,'-',city,'_RF_',varname,'_worldpop_testdata.csv')))
  #testdataADD_ means testdataADD remove outliers, with difference between pred and actual larger than 5
  testdataADD_ <- testdataADD[-c(indexout),]
  write.csv(testdataADD_,file=paste0(pathre,paste0(traincity,'-',city,'_RF_',varname,'_worldpop_testdata_withoutoutlier.csv')))
  ###############################################################
  testdata_new <- testdata[-c(indexout),]
  pred_new <- pred[-c(indexout)]
  r2_new <- 1 - (sum((testdata_new$diff-pred_new)^2)/sum((testdata_new$diff-mean(testdata_new$diff))^2))
  mse_new <- mean((testdata_new$diff - pred_new)^2)#mean squared error
  datanew=data.frame(actual=testdata_new$diff, pred=pred_new)
  xylim <- c(min(datanew$actual),min(datanew$pred),max(datanew$actual),max(datanew$pred))
  anno <- paste('~R^2 ==~',format(round(r2_new, 2), nsmall = 2))
  p_new <- ggplot(datanew,aes(x=actual, y=pred))
  p_new <- p_new + geom_point(size=0.5) +
    geom_abline(mapping=aes(intercept = 0, slope = 1,color='red'),linetype='dotted',size=1) +
    #ggtitle('Carlisle')
    ggtitle(titlename)############################################################################

  lmin <- 0
  lmax <- 30
  rx <- 0.4*(lmax-lmin)
  ry <- 0.6*(lmax-lmin)
  p_new <- p_new + scale_y_continuous(breaks=seq(lmin, lmax, 5), limits=c(lmin, lmax))+scale_x_continuous(breaks=seq(lmin, lmax, 5), limits=c(lmin, lmax))+coord_equal()
  p_new <- p_new + annotate(geom="text", x= rx,y=ry,label=anno,parse=T,size=3.5)
  p_new <-p_new+ylab('Predicted error(m)')+xlab('Actual error(m)')
  p_new <- p_new + theme(panel.border = element_blank(),
                         axis.line.x = element_line(size = 0.5, linetype = "solid"),
                         axis.line.y = element_line(size = 0.5, linetype = "solid"))
  p_new <- p_new + theme(plot.title = element_text(hjust = 0.5))
  p_new <- p_new + scale_color_identity(name='',labels=c("Perfect Fit"), guide="legend")
  p_new <- p_new + theme(legend.position=c(0.3,0.95),legend.text=element_text(size=10),
                         plot.title=element_text(size=12))
  print(p_new)
  ggsave(paste0(pathre,paste0(traincity,'-',city,'-RF_',varname,'_worldpop_withoutOutlier5.png')),
         width=3,height=3)########################
  #restrict data to two digits
  #calculate rmse as data after remove outliers
  MERIT_ori <- ds[ind==2,16]############
  MERIT_ori_n <- MERIT_ori[-c(indexout)]
  ds[ind==2,16] <- MERIT_ori- pred######
  ds_1 <- ds#with outlier
  ds[indexout,16] <- MERIT_ori[indexout]#restore the outlier to original MERIT data
  ds_2 <- ds#without outlier
  MERIT_new <- ds_1[ind==2,16]############
  MERIT_new_n <- MERIT_new[-c(indexout)]
  lidar_ma <- ds_1[ind==2,17]#############
  lidar_ma_n <- lidar_ma[-c(indexout)]
  #calculate the rmse of original and new merit
  rmse_ori = rmse(lidar_ma, MERIT_ori)
  rmse_new = rmse(lidar_ma, MERIT_new)
  rmse_ori_n = rmse(lidar_ma_n, MERIT_ori_n)
  rmse_new_n = rmse(lidar_ma_n, MERIT_new_n)
  output <- data.frame('rmse_ori'=rmse_ori,'rmse_new'=rmse_new,'R^2'=r2,'mse'=mse,
                       'traindata'=nrow(traindata),'testdata'=nrow(testdata))
  write.csv(output,file = paste0(pathre,paste0(traincity,'-',city,'_RF_',varname,'_worldpop.csv')))
  #################################################################
  output <- data.frame('rmse_ori'=rmse_ori_n,'rmse_new'=rmse_new_n,'R^2'=r2_new,'mse'=mse_new,
                       'traindata'=nrow(traindata),'testdata'=nrow(testdata))
  write.csv(output,file = paste0(pathre,paste0(traincity,'-',city,'_RF_',
                                               varname,'_worldpop_withoutoutlier.csv')))
  #################################################################
  # pass updated MERITlist value to MERIT raster
  ########################################################################################
  #read data to predict error
  path <-paste0('path of regression datasets',city,'/RF_layers/') ####################################################
  path2 <- paste0('path of regression datasets',city,'/DEMs/')#######################################################
  #read file with tif ending to list
  dem <- list.files(path=path2,pattern = '\\.tif$',full.names = TRUE)
  merit[] <- merit
  #read original MERIT for predict value to update MERIT
  MERITname <- dem[2]
  MERITra <- raster(MERITname)
  MERIT <- as.matrix(MERITra)
  merit[ma_f] <- ds_1[,16]#here the MERIT was updated with predicted error with outlier###########
  MERITlist <- resize(merit,nrow(MERIT)*ncol(MERIT),1)
  MERITra[] <- MERITlist
  writeRaster(MERITra,filename=paste0(pathre,paste0(traincity,'-',city,'_MERIT_',varname,'_worldpop_update.tif'))######
              , format="GTiff",overwrite=TRUE)
  merit[ma_f] <- ds_2[,16]#here the MERIT was updated with predicted error without outlier UPDATED###########
  MERITlist <- resize(merit,nrow(MERIT)*ncol(MERIT),1)
  MERITra[] <- MERITlist
  writeRaster(MERITra,filename=paste0(pathre,paste0(traincity,'-',city,'_MERIT_',varname,'_worldpop_update_out.tif'))######
              , format="GTiff",overwrite=TRUE)
}
############################################################ Cambridge
city <- city6
traincity <- paste(city6,sep=' ')
pathre <- paste0('outputpath',
                 traincity,'-',city,'/')
if (!dir.exists(pathre)){dir.create(pathre)}
ds <- ds6
regression(city,traincity,pathre,ds,ma_f6,merit6,0.025)
############################################# Bristol
city <- city2
traincity <- city2
pathre <- paste0('outputpath',
                 traincity,'-',city,'/')
if (!dir.exists(pathre)){dir.create(pathre)}
ds <- ds2
regression(city,traincity,pathre,ds,ma_f2,merit2,0.025)
############################################# Manchester
city <- city1
traincity <- city1
pathre <- paste0('outputpath',
                 traincity,'-',city,'/')
if (!dir.exists(pathre)){dir.create(pathre)}
ds <- ds1
regression(city,traincity,pathre,ds,ma_f1,merit1,0.025)
############################################# London
city <- city3
traincity <- city3
pathre <- paste0('outputpath',
                 traincity,'-',city,'/')
if (!dir.exists(pathre)){dir.create(pathre)}
ds <- ds3
regression(city,traincity,pathre,ds,ma_f3,merit3,0.025)

############################################# Beijing
city <- city4
traincity <- city4
pathre <- paste0('outputpath',
                 traincity,'-',city,'/')
if (!dir.exists(pathre)){dir.create(pathre)}
ds <- ds4
regression(city,traincity,pathre,ds,ma_f4,merit4,0.025)
########################################## Carlisle
city7 <- 'Carlisle'
#minmum rectangle of major town and cities in Carlisle was taken as the
#boundary of Carlisle_boun here
city <- city7
traincity <- city7
pathre <- paste0('outputpath',
                 traincity,'-',city,'/')
if (!dir.exists(pathre)){dir.create(pathre)}
ds <- ds7
merit <- merit7
ma_f <- ma_f7
regression(city,traincity,pathre,ds,ma_f,merit,0.025)

############################################# Berlin non forest
city <- city5
traincity <- city5
pathre <- paste0('outputpath',
                 traincity,'-',city,'/')
if (!dir.exists(pathre)){dir.create(pathre)}
ds <- ds5
regression(city,traincity,pathre,ds,ma_f5,merit5,0.025)