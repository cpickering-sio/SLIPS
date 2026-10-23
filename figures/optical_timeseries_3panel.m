%% optical_timeseries_3panel.m
% 3-panel time series of optical-clarity metrics by treatment.
% Each point/line = mean of the (up to 4) cameras in a treatment on that day.
% Uncertainty = standard error (SD / sqrt(n_cameras that day)), shown either as
% error bars or a shaded band (set STYLE below).  Style of plot_optics_vs_env.m.
clear; clc; close all;

%% ---- config -------------------------------------------------------------
imgCsv = '/Volumes/samsung/Corinne/SLIPS082026/coral_cams/ROI_crops/biofouling_master.csv';
metrics   = ["Michelson Contrast","Laplacian Variance","Intensity Std"];   % exact column names
metricLab = ["Michelson contrast","Laplacian variance","Intensity std (\sigma)"];
treatments = ["Acrylic","Glass","SLIPS"];
% colours match the dry-mass + plot_optics_vs_env figures
tcol = containers.Map({'Acrylic','Glass','SLIPS'}, ...
       {[0.44 0.68 0.28],[0.88 0.48 0.33],[0.36 0.61 0.84]});

STYLE         = "band";    % <<< "band" (shaded SE) or "errorbar"
BASELINE_NORM = false;     % <<< TRUE = within-camera change from day 0 (Michelson/Laplacian)

%% ---- load + prep --------------------------------------------------------
T = readtable(imgCsv,'VariableNamingRule','preserve');
T.Date      = datetime(string(T.Date),'InputFormat','yyyy-MM-dd');
T.Day       = days(T.Date - min(T.Date));
T.Treatment = categorical(string(T.Treatment));
T.Camera    = categorical(T.Camera);

%% ---- figure -------------------------------------------------------------
figure('Color','w','Position',[80 80 1320 420]);
tl = tiledlayout(1, numel(metrics), 'TileSpacing','compact','Padding','compact');

for mi = 1:numel(metrics)
    y = T.(char(metrics(mi)));

    if BASELINE_NORM                         % within-camera change from first day
        cams = categories(T.Camera);
        for c = 1:numel(cams)
            idx = T.Camera==cams{c};  di = find(idx);
            [~,first] = min(T.Day(idx));
            y(idx) = y(idx) - y(di(first));
        end
    end

    Tm = T; Tm.y = y;
    G = groupsummary(Tm, {'Treatment','Day'}, {'mean','std'}, 'y');
    G.se = G.std_y ./ sqrt(G.GroupCount);    % SE from actual n cameras that day

    nexttile; hold on
    for k = 1:numel(treatments)
        t    = treatments(k);
        col  = tcol(char(t));
        rows = string(G.Treatment)==t;
        [dd,ord] = sort(G.Day(rows));
        mu = G.mean_y(rows);  mu = mu(ord);
        se = G.se(rows);      se = se(ord);
        ok = ~isnan(mu);  dd=dd(ok); mu=mu(ok); se=se(ok);  se(isnan(se))=0;

        if STYLE == "band"
            fill([dd; flipud(dd)], [mu+se; flipud(mu-se)], col, ...
                 'FaceAlpha',0.18, 'EdgeColor','none', 'HandleVisibility','off');
            plot(dd, mu, '-', 'Color',col, 'LineWidth',1.8, 'DisplayName',char(t));
        else
            errorbar(dd, mu, se, '-o', 'Color',col, 'MarkerFaceColor',col, ...
                     'MarkerSize',4, 'LineWidth',1.5, 'CapSize',3, 'DisplayName',char(t));
        end
    end
    xlabel('Day of deployment'); ylabel(metricLab(mi)); grid on; box on
    title(metricLab(mi),'Interpreter','tex')
    if mi==1, legend('Location','best'); end
end
title(tl, 'Optical clarity by treatment over time  (mean \pm SE, n = 4 cameras)', ...
      'FontWeight','bold','Interpreter','tex')

% save as editable vector PDF:
% exportgraphics(gcf,'optical_timeseries_3panel.pdf','ContentType','vector')
