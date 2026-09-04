import os
import glob
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm

def generate_meteologix_style_maps(grib_folder, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    file_pattern = os.path.join(grib_folder, "*.grib2")
    files = sorted(glob.glob(file_pattern))

    if not files:
        print("❌ لم يتم العثور على ملفات grib2")
        return

    # التدرج اللونية المستوحى من Meteologix لتراكم الأمطار
    colors = [
        '#ffffff', '#dbeedb', '#b5e3b5', '#8cd58c', '#52c352', 
        '#00a800', '#008800', '#006400', '#ffff00', '#e6c200', 
        '#ff9900', '#ff0000', '#cc0000', '#990000', '#e000e0', '#800080'
    ]
    levels = [0, 0.2, 1, 2, 5, 10, 15, 20, 30, 40, 50, 75, 100, 150, 200, 300]
    
    cmap = LinearSegmentedColormap.from_list('meteologix_precip', colors, len(levels) - 1)
    norm = BoundaryNorm(levels, cmap.N)

    accumulated_rain = None

    for i, file_path in enumerate(files):
        try:
            ds = xr.open_dataset(file_path, engine='cfgrib', backend_kwargs={'filter_by_keys': {'shortName': 'refc'}})
            dbz = ds['refc'].values
            
            # تحويل dBZ إلى معدل هطول (mm/hr)
            clean_dbz = np.maximum(dbz, 0)
            z = 10.0 ** (clean_dbz / 10.0)
            rain_rate = np.where(dbz < 15, 0, (z / 200.0) ** (1.0 / 1.6))
            
            # تراكمي الساعات (حساب فارق الساعة)
            if accumulated_rain is None:
                accumulated_rain = rain_rate
            else:
                accumulated_rain += rain_rate

            fig = plt.figure(figsize=(14, 9), facecolor='#1e1e1e')
            ax = plt.axes(projection=ccrs.PlateCarree())
            ax.set_facecolor('#111111')

            lons = ds.longitude.values
            lats = ds.latitude.values

            # رسم الأمطار
            im = ax.contourf(lons, lats, accumulated_rain, levels=levels, cmap=cmap, norm=norm, extend='max', transform=ccrs.PlateCarree())

            # إضافة حدود جغرافية بنفس طابع Meteologix الداكن
            ax.add_feature(cfeature.COASTLINE, color='#aaaaaa', linewidth=0.8)
            ax.add_feature(cfeature.BORDERS, color='#888888', linewidth=0.6, linestyle=':')
            
            ax.set_extent([41, 55, 12, 20], crs=ccrs.PlateCarree())

            # إضافة شريط المقياس
            cbar = plt.colorbar(im, ax=ax, orientation='horizontal', pad=0.04, shrink=0.7)
            cbar.set_label('Total Precipitation / التراكمي (mm)', color='white')
            cbar.ax.xaxis.set_tick_params(color='white')
            plt.setp(plt.getp(cbar.ax, 'xticklabels'), color='white')

            plt.title(f"GFS Model - Total Accumulated Precipitation (+{i+1}h)", color='white', fontsize=14, pad=12)

            f_num = f"{i+1:03d}"
            save_path = os.path.join(output_dir, f"precip_f{f_num}.png")
            plt.savefig(save_path, bbox_inches='tight', facecolor='#1e1e1e', dpi=150)
            plt.close()
            print(f"✓ تم توليد الخريطة: {save_path}")

        except Exception as e:
            print(f"⚠ خطأ في معالجة {file_path}: {e}")

if __name__ == "__main__":
    generate_meteologix_style_maps(
        grib_folder=r"./GFS_REFC_Yemen_20260904_12z", 
        output_dir=r"./static/maps"
    )