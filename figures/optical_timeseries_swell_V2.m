%% optical_timeseries_swell.m
% THREE figures of the optical-clarity time series (treatment mean +/- SE bands,
% LEFT axis) with CDIP swell overlaid on a RIGHT-hand y-axis:
%   Fig 1 : swell HEIGHT  (H_s, real metres)
%   Fig 2 : swell PERIOD  (T_p, real seconds)
%   Fig 3 : BOTH, standardized (z-score) on one shared axis
% Swell is shown as a 6-hour rolling mean (solid line) with a +/- SE band.
% A near-bed orbital-velocity line (u_b) is pre-computed and left COMMENTED
% (placeholder) -> uncomment in Fig 3 when ready.
%
% Adapted from optical_timeseries_3panel.m + plot_optics_vs_env.m.
clear; clc; close all;

%% ---- config -------------------------------------------------------------
imgCsv  = '/Volumes/samsung/Corinne/SLIPS082026/coral_cams/ROI_crops/biofouling_master.csv';
cdipURL = 'https://thredds.cdip.ucsd.edu/thredds/dodsC/cdip/realtime/201p1_rt.nc';
metrics   = ["Michelson Contrast","Laplacian Variance","Intensity Std"];
metricLab = ["Michelson contrast","Laplacian variance","Intensity std (\sigma)"];
treatments = ["Acrylic","Glass","SLIPS"];
tcol = containers.Map({'Acrylic','Glass','SLIPS'}, ...
       {[0.44 0.68 0.28],[0.88 0.48 0.33],[0.36 0.61 0.84]});
BASELINE_NORM = false;              % TRUE = within-camera change (Michelson/Laplacian)
SITE_DEPTH    = 12;                 % <<< metres: YOUR deployment depth (CONFIRM) --
                                    %     only used by the u_b placeholder below
WIN = hours(6);                     % rolling-mean window for swell

swcol_Hs=[0.25 0.25 0.25]; swcol_Tp=[0.55 0.20 0.60]; swcol_ub=[0.60 0.35 0.10];

%% ---- load optical metrics ----------------------------------------------
T = readtable(imgCsv,'VariableNamingRule','preserve');
T.Date = datetime(string(T.Date),'InputFormat','yyyy-MM-dd');
T.Treatment = categorical(string(T.Treatment)); T.Camera = categorical(T.Camera);
d0 = min(T.Date); T.Daynum = days(T.Date - d0);

%% ---- CDIP swell at native (high) resolution ----------------------------
tt = ncread(cdipURL,'waveTime'); Hs = ncread(cdipURL,'waveHs'); Tp = ncread(cdipURL,'waveTp');
swTime = datetime(1970,1,1) + seconds(tt);
win = swTime >= d0 & swTime <= max(T.Date)+days(1);
swTime = swTime(win); Hs = Hs(win); Tp = Tp(win);
Hs(Hs>50)=NaN; Tp(Tp>100)=NaN;      % CDIP fill values
fprintf('CDIP sampling interval: %.0f min  (%d samples in window)\n', ...
        minutes(median(diff(swTime),'omitnan')), numel(swTime));
swx = days(swTime - d0);
zs  = @(v)(v - mean(v,'omitnan'))./std(v,'omitnan');
Hs_z = zs(Hs); Tp_z = zs(Tp);

% near-bed orbital velocity (PLACEHOLDER): linear wave theory at SITE_DEPTH
k  = wavenum(Tp, SITE_DEPTH);
ub = pi*Hs ./ (Tp .* sinh(k*SITE_DEPTH));   ub_z = zs(ub);   % m/s

% ---- 6-hr rolling mean +/- SE for each swell series ----
[Hs_m, Hs_se]   = rollstat(Hs,   swTime, WIN);
[Tp_m, Tp_se]   = rollstat(Tp,   swTime, WIN);
[Hsz_m,Hsz_se]  = rollstat(Hs_z, swTime, WIN);
[Tpz_m,Tpz_se]  = rollstat(Tp_z, swTime, WIN);
[ubz_m,ubz_se]  = rollstat(ub_z, swTime, WIN);   % placeholder (z-units)

%% ---- build the three figures -------------------------------------------
modes  = ["Hs","Tp","both_z"];
figttl = ["Optical clarity with swell height overlay", ...
          "Optical clarity with swell period overlay", ...
          "Optical clarity with standardized swell (height & period)"];
for f = 1:numel(modes)
    mo = modes(f);
    figure('Color','w','Position',[40 60 1420 450]);
    tl = tiledlayout(1,numel(metrics),'TileSpacing','compact','Padding','compact');
    for mi = 1:numel(metrics)
        y = T.(char(metrics(mi)));
        if BASELINE_NORM
            cams=categories(T.Camera);
            for c=1:numel(cams)
                idx=T.Camera==cams{c}; di=find(idx); [~,ff]=min(T.Daynum(idx)); y(idx)=y(idx)-y(di(ff));
            end
        end
        Tm=T; Tm.y=y;
        G = groupsummary(Tm,{'Treatment','Daynum'},{'mean','std'},'y'); G.se=G.std_y./sqrt(G.GroupCount);

        nexttile; hold on
        % ---- RIGHT axis: swell (6-h rolling mean + SE band), drawn first ----
        yyaxis right
        switch mo
            case "Hs"
                drawband(swx, Hs_m, Hs_se, swcol_Hs, 1.8, 'Swell height H_s (m)');
                ylabel('Swell height  H_s (m)');
            case "Tp"
                drawband(swx, Tp_m, Tp_se, swcol_Tp, 1.8, 'Swell period T_p (s)');
                ylabel('Swell period  T_p (s)');
            case "both_z"
                drawband(swx, Hsz_m, Hsz_se, swcol_Hs, 1.8, 'H_s (std.)');
                drawband(swx, Tpz_m, Tpz_se, swcol_Tp, 1.8, 'T_p (std.)');
                % --- near-bed orbital velocity (uncomment to add) ---
                % drawband(swx, ubz_m, ubz_se, swcol_ub, 1.8, 'u_b (std.)');
                ylabel('swell (standardized, z-score)');
        end
        set(gca,'YColor',[0.3 0.3 0.3]);

        % ---- LEFT axis: metric mean +/- SE band per treatment ----
        yyaxis left
        for kk = 1:numel(treatments)
            t_=treatments(kk); col=tcol(char(t_)); rows=string(G.Treatment)==t_;
            [dd,ord]=sort(G.Daynum(rows)); mu=G.mean_y(rows); mu=mu(ord); se=G.se(rows); se=se(ord);
            ok=~isnan(mu); dd=dd(ok); mu=mu(ok); se=se(ok); se(isnan(se))=0;
            fill([dd;flipud(dd)],[mu+se;flipud(mu-se)],col,'FaceAlpha',0.15,'EdgeColor','none','HandleVisibility','off');
            plot(dd,mu,'-','Color',col,'LineWidth',1.8,'DisplayName',char(t_));
        end
        ylabel(metricLab(mi)); set(gca,'YColor','k');
        xlabel('Day of deployment'); grid on; box on; title(metricLab(mi),'Interpreter','tex');
        if mi==1
            legend('Location','northoutside','Orientation','horizontal','NumColumns',5,'FontSize',8);
        end
    end
    title(tl, figttl(f) + "  (swell: 6-h rolling mean \pm SD)", 'FontWeight','bold','Interpreter','tex');
    % exportgraphics(gcf, "optical_swell_"+mo+".pdf", 'ContentType','vector');
end

%% ---- local functions ----------------------------------------------------
function [m, se] = rollstat(v, t, win)
    % 6-h (window=win) rolling mean and standard error, on irregular SamplePoints
    m  = movmean(v, win, 'omitnan', 'SamplePoints', t);
    sd = movstd (v, win, 0, 'omitnan', 'SamplePoints', t);
    n  = movsum (double(~isnan(v)), win, 'SamplePoints', t);
    se = sd; %./ sqrt(max(n,1)); <-convert from SE to SD 
end

function drawband(x, m, se, col, lw, name)
    x=x(:); m=m(:); se=se(:);
    ok = ~isnan(m) & ~isnan(se);
    xo=x(ok); mo=m(ok); so=se(ok);
    fill([xo; flipud(xo)], [mo+so; flipud(mo-so)], col, ...
         'FaceAlpha',0.15, 'EdgeColor','none', 'HandleVisibility','off');
    plot(x, m, '-', 'Color', col, 'LineWidth', lw, 'DisplayName', name);
end

function k = wavenum(T, d)
    g = 9.81; w = 2*pi./T; k = w.^2/g;              % deep-water start
    for it = 1:100, k = w.^2 ./ (g*tanh(k.*d)); end % iterate to convergence
end
