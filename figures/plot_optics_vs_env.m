%% plot_optics_vs_env.m
% =========================================================================
% SLIPS Off-Pier 2026 — time series of an OPTICAL CLARITY metric (by
% treatment) overlaid on CDIP environmental covariates (double-Y).
%
% Left Y  = chosen optical metric, averaged over the 4 cameras per treatment
%           (3 lines: Acrylic / Glass / SLIPS)
% Right Y = an environmental covariate (swell height, swell period, ... )
% One panel per environmental covariate, sharing the date axis.
%
% Built from the working session in biofouling_session_log.txt:
%   - image metrics come from biofouling_master.csv (table T)
%   - swell comes from CDIP station 201p1 REALTIME NetCDF (the historic
%     archive did not yet cover Aug–Sep 2026)
%
% HOW TO SWAP THE OPTICAL VARIABLE (contrast -> variance -> intensity):
%   edit the metricList on the line flagged  <<< CHANGE OPTICAL METRIC HERE >>>
% =========================================================================
clear; clc; close all;

%% ---- 0. PATHS (edit to match your machine) --------------------------------
imgCsv = 'biofouling_master.csv';   % the per-image metric master (table T)
% If it's not on the MATLAB path / current folder, give the full path, e.g.:
% imgCsv = '/Volumes/samsung/Corinne/SLIPS082026/coral_cams/ROI_crops/biofouling_master.csv';

%% ---- 1. LOAD IMAGE METRICS ------------------------------------------------
T = readtable(imgCsv, 'VariableNamingRule','preserve');   % keep spaced names
if ~isdatetime(T.Date)
    T.Date = datetime(string(T.Date), 'InputFormat','yyyy-MM-dd');
end

%% ---- 2. FETCH SWELL (CDIP 201p1 realtime) ---------------------------------
% realtime file covers the last ~months (historic lagged behind Aug–Sep 2026).
Wd = fetchSwellDaily('https://thredds.cdip.ucsd.edu/thredds/dodsC/cdip/realtime/201p1_rt.nc', ...
                     datetime(2026,8,21), datetime(2026,9,21));
fprintf('Swell days with data: %d\n', sum(~isnan(Wd.Hs)));

%% ---- 3. CHOOSE WHAT TO PLOT -----------------------------------------------
% <<< CHANGE OPTICAL METRIC HERE >>>  (must match a column name in T exactly)
% Options present in biofouling_master.csv:
%   "Michelson Contrast" | "Laplacian Variance" | "Intensity Std"
%   "Histogram Entropy"  | "SSIM" | "PSNR" | "Delta E 2000"
% Put ONE name for a single figure, or several to generate one figure each.
metricList = ["Michelson Contrast", "Laplacian Variance", "Intensity Std"];

% Environmental covariates to put on the RIGHT axis (one panel each).
% Column names must exist in Wd ('Hs' = swell height m, 'Tp' = swell period s).
envVars   = ["Hs",                 "Tp"];
envLabels = ["Swell height  H_s (m)", "Swell period  T_p (s)"];

%% ---- 4. MAKE THE PLOTS ----------------------------------------------------
for m = 1:numel(metricList)
    plotMetricVsEnv(T, metricList(m), Wd, envVars, envLabels);
    % to save each figure, uncomment:
    % exportgraphics(gcf, "ts_" + matlab.lang.makeValidName(metricList(m)) + ".png", 'Resolution',200);
end


%% =========================================================================
%  LOCAL FUNCTIONS  (no edits needed below for a routine metric swap)
%  =========================================================================

function Wd = fetchSwellDaily(url, dStart, dEnd)
% Read CDIP wave params over OPeNDAP, clip to [dStart,dEnd), daily-mean.
    t  = ncread(url,'waveTime');                 % seconds since 1970 UTC
    Hs = ncread(url,'waveHs');                    % significant wave height (m)
    Tp = ncread(url,'waveTp');                    % peak period (s)
    time = datetime(1970,1,1,0,0,0) + seconds(t); % zone-less (matches image dates)

    W = timetable(time, Hs, Tp);
    W = W(timerange(dStart, dEnd), :);
    W.Hs(W.Hs > 50)  = NaN;                       % CDIP fill value = 9999
    W.Tp(W.Tp > 100) = NaN;
    Wd = retime(W,'daily','mean');                % use 'max' for daily PEAK swell
end


function TTm = metricByTreatment(T, metricName)
% Average the 4 cameras per treatment per day -> wide timetable
% (columns = treatments: Acrylic, Glass, SLIPS; rows = Date).
    G  = groupsummary(T, ["Treatment","Date"], "mean", metricName);
    mc = "mean_" + metricName;                    % groupsummary output column
    W  = unstack(G(:,["Treatment","Date",mc]), mc, "Treatment");
    TTm = table2timetable(W, "RowTimes","Date");
    % --- NOTE: for reference metrics (SSIM/PSNR/Delta E), the baseline day
    %     2026-08-21 is trivial (SSIM=1, DeltaE=0) and flattens the axis.
    %     Uncomment to drop it:
    % TTm(TTm.Date==datetime(2026,8,21),:) = [];
end


function plotMetricVsEnv(T, metricName, envTT, envVars, envLabels)
% Left Y = metric by treatment (3 lines); Right Y = each env covariate (1 panel each).
    TTm = metricByTreatment(T, metricName);
    trt = string(TTm.Properties.VariableNames);       % treatment column names
    dMetric = TTm.Properties.RowTimes;
    dEnv    = envTT.Properties.RowTimes;

    % fixed colour per treatment (stable regardless of column order)
    tcol = containers.Map({'Acrylic','Glass','SLIPS'}, ...
           {[0.44 0.68 0.28],[0.88 0.48 0.33],[0.36 0.61 0.84]});
    getCol = @(name) tcol(char(name));

    nP = numel(envVars);
    figure('Color','w','Position',[80 80 650*nP 500]);
    tl = tiledlayout(1, nP, 'TileSpacing','compact','Padding','compact');

    for p = 1:nP
        nexttile
        % LEFT: optical metric, one line per treatment
        yyaxis left; hold on
        for k = 1:numel(trt)
            plot(dMetric, TTm.(trt(k)), '-o', 'LineWidth',1.6, ...
                 'MarkerSize',3, 'Color', getCol(trt(k)));
        end
        ylabel(metricLabel(metricName)); set(gca,'YColor','k')

        % RIGHT: environmental covariate
        yyaxis right
        plot(dEnv, envTT.(envVars(p)), '--k', 'LineWidth',1.6);
        ylabel(envLabels(p)); set(gca,'YColor','k')

        xlabel('Date'); grid on
        title(metricLabel(metricName) + " vs. " + envLabels(p), 'Interpreter','none');
    end

    legend([trt, "env"], 'Location','southoutside','Orientation','horizontal');
    title(tl, metricName + " by treatment vs. CDIP 201p1 swell", 'Interpreter','none');
    linkaxes(findobj(tl,'Type','axes'),'x');
end


function lab = metricLabel(metricName)
% Pretty axis label for the common metrics; defaults to the raw name.
    switch string(metricName)
        case "Michelson Contrast", lab = "Michelson contrast";
        case "Laplacian Variance", lab = "Laplacian variance";
        case "Intensity Std",      lab = "Intensity std (\sigma)";
        case "Histogram Entropy",  lab = "Histogram entropy";
        otherwise,                 lab = string(metricName);
    end
end
