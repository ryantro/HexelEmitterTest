% Takes a 2D frequency distribution and stacks all the data into a 1D array for
% descriptive statistics calculations

clear all
clc
close all


[data,txt] = xlsread('N:\SOFTWARE\Python\hexelemittertest\hexelemittertest\testdata\Hexel1002570-20220208-102829\emitter-1\dc-99.csv');

data(:,2) = data(:,2) - mean(data(end-2000:end,2));

% find the peak maximum
indexMax = find(data(:,2) == max(data(:,2)));

% find the wavelength per bin
dWL = (data(end,1) - data(1,1))/numel(data(:,1));


Distribution = [];  % Used to stack all the data into a 1D array for skew and kurt calcs (Initialize variable container)
indexData = 1;
for i = int16(indexMax - 10/dWL):int16(indexMax + 10/dWL)  % only calculate from -10 nm to +10 nm from the peak (save time)
    for j = 1:data(i,2)
        Distribution(indexData) = data(i,1);  % could be much faster with vector notation, but leave this way for clarity 
        indexData = indexData + 1;
    end
end % for i

fprintf('Skew: %f             Kurtosis: %f\n',skewness(Distribution),kurtosis(Distribution))

