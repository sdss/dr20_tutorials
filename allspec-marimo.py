import marimo

__generated_with = "0.15.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""# Checking whether SDSS has a spectrum for me""")
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Learning goals

    Through this tutorial, you will learn:

     * How to use the "allspec" file either locally or on SciServer to check whether an object you are interested in has SDSS spectra.
     * How to track down the relevant SDSS-V BOSS (optical) parameters and spectrum for galaxies and quasars.
     * How to track down the relevant SDSS-V BOSS (optical) and APOGEE (infrared) parameters and spectrum for stars.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Introduction

    SDSS has observed spectra in several ways over the past 20+ years. Specifically, we have used the SDSS and BOSS optical spectrographs in single-fiber and integral-field modes, and we have used the two APOGEE spectrographs in single-fiber mode. Meanwhile, this data has been processed through a several pipelines and pipeline stages, and is processed into both individual visit and coadded spectra.

    To help users track down the relevant information for objects of interest, SDSS has created the `allspec` file. This file lists all spectra that SDSS has created, including all visit spectra and all coadds from every spectrograph. In this file, every object may appear once or more, if they have multiple spectra. 

    Objects in SDSS are tracked through the `sdss_id` identifier. This is designed to correspond to unique objects on the sky, and in this notebook we will use it to identify the "same object" across different spectra.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Imports

    We will need several Python modules for our tasks:

     * `os` because we usually need it
     * `matplotlib.pyplot` for plotting
     * `matplotlib` because I'm persnickety about TeXing labels
     * `numpy` because we have to do things with numbers and arrays
     * `astropy.io.fits` to read spectra files
     * `fitsio` for efficiently reading very large files (spAll, specObjAll)
     * `astropy.coordinates` for spatial matching
     * `sdss_access` to track down files
     * `polars` for reading in the very large allspec file
     * `scipy` part of `astropy[all]`, otherwise needed on it's own for coordinate matching

     #### Caveats: 
     If you are running this notebook on your own machine, there are few things you should make note of:

     1. Some of the files loaded in this notebook are very large and use a lot of RAM (seriously: > 32 GB RAM is required, we recommend running this notebook on sciserver)
     2. If you don't have a properly configured Tex distrubution, you may need to comment out the line `matplotlib.rcParams['text.usetex'] = True` in the imports cell.
     3. The first time you check for a local file on your "local" "SAS", the filename may be created as `.fits` whereas the downloaded file may be `.fits.gz`. Re-running the cell fixes the problem.

    #### A note about parquet files

    For DR20, a parquet version of the allspec file has been made available. Using the parquet file results in reading the file more than 10x faster, and also uses roughly half as much memory compared to the fits file. These efficiency gains make parquet files an easy choice. There are a few minor type castings as a result.
    """
    )
    return


@app.cell
def _():
    import os
    import matplotlib
    import matplotlib.pyplot as plt
    import numpy as np
    import astropy.io.fits
    import astropy.coordinates
    import fitsio
    import polars
    import sdss_access

    #os.environ["SAS_BASE_DIR"] = os.path.expanduser("/data/sdss")
    matplotlib.rcParams['text.usetex'] = True
    matplotlib.rcParams['font.size'] = 14
    return astropy, np, os, plt, polars, sdss_access


@app.cell
def _(mo):
    mo.md(
        r"""
    ## SDSS File Access

    `sdss_access` provides ways to track down SDSS files in the data structure. 

    This notebook is perhaps easiest to run on SciServer. But if you are working on a machine without a full copy of the SDSS Science Archive Server (SAS), you can set it up to download and cache files locally. See https:://https://sdss-access.readthedocs.io for more information!
    """
    )
    return


@app.cell
def _(sdss_access):
    sdss_path = sdss_access.path.Path(release='dr20', verbose=True)
    access = sdss_access.Access(release='dr20', verbose=True)
    return access, sdss_path


@app.cell
def _(mo):
    mo.md(r"""## Finding and Reading the `allspec` file""")
    return


@app.cell
def _(mo):
    mo.md(r"""`sdss_path` gives us an easy way to find the path to the `allspec` file.""")
    return


@app.cell
def _(access, sdss_path):
    allspec_file = sdss_path.full('allspec', vers='1.0.2', release='dr20', ftype="parquet")

    if not sdss_path.exists('',full=allspec_file):
        # if the file does not exist locally, this code will download the data.
        access.remote()
        access.add('allspec', vers='1.0.2', release='dr20', ftype="parquet")
        access.set_stream()
        access.commit()
        allspec_file = sdss_path.full('allspec', vers='1.0.2', release='dr20', ftype="parquet")
    return (allspec_file,)


@app.cell
def _(allspec_file, os):
    exists = os.path.isfile(allspec_file)
    print("Allspec file path:", allspec_file)
    print("File exists locally:", exists)
    return


@app.cell
def _(allspec_file, polars):
    allspec = polars.read_parquet(allspec_file)
    print("Successfully loaded allspec dataset shape:", allspec.shape)
    print("First 5 rows preview:")
    print(allspec.head(5))
    return (allspec,)


@app.cell
def _(mo):
    mo.md(r"""## Matching by position to `allspec`""")
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    Let's say we have some position of interest. Let's figure out if we have SDSS spectra of any sort near it!

    I like the location (ra, dec) = (177.78, -0.73), just because I do. Let's put this in the `astropy.coordinates.SkyCoord` object.
    """
    )
    return


@app.cell
def _(astropy):
    center_ra = [103.40819321]
    center_dec = [-1.32137059392]
    center_coords = astropy.coordinates.SkyCoord(center_ra, center_dec, unit='deg', frame='icrs')
    return (center_coords,)


@app.cell
def _(mo):
    mo.md(r"""Each `sdss_id` has a specific RA and Dec, so we only need to match to the unique set of `sdss_id`s. We will put those coordinates into the `astropy` object too.""")
    return


@app.cell
def _(allspec, astropy, np):
    unique_sdss_id, _unique_indx_raw = np.unique(allspec['sdss_id'], return_index=True)
    _unique_ra_raw = np.array(allspec['ra'][_unique_indx_raw])
    _unique_dec_raw = np.array(allspec['dec'][_unique_indx_raw])

    # There are a few NaNs as coordinates that need to be removed. 
    isfinite = np.isfinite(_unique_ra_raw) & np.isfinite(_unique_dec_raw)
    unique_indx = _unique_indx_raw[isfinite]
    unique_ra = _unique_ra_raw[isfinite]
    unique_dec = _unique_dec_raw[isfinite]
    unique_coords = astropy.coordinates.SkyCoord(unique_ra, unique_dec, unit='deg', frame='icrs')
    return unique_coords, unique_indx


@app.cell
def _(mo):
    mo.md(r"""Now it is easy to match. Let's look at the closest one to our desired position.""")
    return


@app.cell
def _(center_coords, unique_coords):
    indx, _sep, s3 = unique_coords.match_to_catalog_sky(center_coords)
    sep = _sep.value   # avoid units nonsense ("value" is in deg in this case)
    return (sep,)


@app.cell
def _(allspec, np, sep, unique_indx):
    iminsep = np.argmin(sep)
    match_indx = int(unique_indx[iminsep])
    sdss_id = allspec['sdss_id'][match_indx]
    print("Match index in unique list (iminsep):", iminsep)
    print("Matched row index in allspec (match_indx):", match_indx)
    print("Matched SDSS ID:", sdss_id)
    print("Separation (arcsec):", sep[iminsep] * 3600.0)
    return (match_indx,)


@app.cell
def _(mo):
    mo.md(r"""## Information in allspec""")
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    Now that we have found a spectrum, we can take a look at the information in `allspec`. Below you can see several types of information:

     * The `allspec` and `multiplex` identifiers (just unique identifiers)
     * Information about the observatory, SDSS phase, and instrument
     * The `sdss_id` and `catalogid` of the target object.
     * Many columns of spectroscopic IDs. Only one set of identifiers will be filled with meaningful information.
     * The name and location of the spectrum file (useful!) and a link to SkyServer
    """
    )
    return


@app.cell
def _(allspec, match_indx):
    for n in allspec.columns:
        print("{n} :: {v}".format(n=n, v=allspec[n][match_indx]))
    return


@app.cell
def _(mo):
    mo.md(r"""## Finding all spectra""")
    return


@app.cell
def _(mo):
    mo.md(r"""We can also find all of the spectra associated with the `sdss_id`. This is useful for objects with repeat spectroscopy.""")
    return


@app.cell
def _(allspec, match_indx, np):
    iallmatch = np.where(allspec['sdss_id'] == allspec['sdss_id'][match_indx])[0]
    print("Matched spectrum indices array (iallmatch):", iallmatch)
    print("Total matching spectra count:", len(iallmatch))
    return (iallmatch,)


@app.cell
def _(mo):
    mo.md(
        r"""
    We can look at what these spectra actually are. It can take some getting used to to figure out this information. What the IDs tell us is:

     * There are three distinct BOSS spectra, which were taken during SDSS-V.
     * We can see that for each MJD (59654 through 59656) there is both a "daily" and an "epoch" coadd. Apparently, the BOSS pipeline considers (for this type of object) that two different days are two different epochs. In this case the "daily" and "epoch" coadds will be very very similar.
     * There are four distinct APOOGEE spectra, and one coadd.
    """
    )
    return


@app.cell
def _(allspec, iallmatch):
    print(allspec['allspec_id'][iallmatch])
    return


@app.cell
def _(mo):
    mo.md(r"""## Looking at the spectra""")
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    We can track down the spectra on disk quite easily. The `sas_url` tells us the path. We just need to change the root of the tree to a local file path as follows.

    If the data don't already exist on disk (e.g., if you're not running this notebook on SciServer), we can download the data easily with `sdss_access`
    """
    )
    return


@app.cell
def _(allspec, iallmatch, os, sdss_access):
    url_root = 'https://data.sdss.org/sas'
    local_root = os.getenv('SAS_BASE_DIR')
    if local_root is None:
        local_root = ""
    spectrum_files = list()
    download_files_dr19 = list()
    download_files_dr20 = list()

    for p in allspec["sas_url"][iallmatch]:
        local_path = p.replace(url_root, local_root)
        spectrum_files.append(local_path)
        if not os.path.exists(local_path):
            if "dr19" in local_path:
                download_files_dr19.append(local_path)
            else:
                download_files_dr20.append(local_path)

    if len(download_files_dr19) > 0:
        access_dl1 = sdss_access.Access(release='dr20', verbose=True)
        print("fetching files, please stand by")
        access_dl1.remote()
        for local_path in download_files_dr19:
            access_dl1.add_file(local_path, input_type='filepath')

        access_dl1.set_stream()

        # disable follow_symlinks
        access_dl1.commit(follow_symlinks=True)

    if len(download_files_dr20) > 0:
        access_dl2 = sdss_access.Access(release='dr20', verbose=True)
        print("fetching files, please stand by")
        access_dl2.remote()
        for local_path in download_files_dr20:
            access_dl2.add_file(local_path, input_type='filepath')

        access_dl2.set_stream()

        # disable follow_symlinks
        access_dl2.commit(follow_symlinks=True)
    return (spectrum_files,)


@app.cell
def _(mo):
    mo.md(r"""Here then are the paths in the local SAS directory structure:""")
    return


@app.cell
def _(os, spectrum_files):
    for i, f in enumerate(spectrum_files):
        # if not os.path.exists(f):
            # spectrum_files[i] += ".gz"
        print(f, os.path.exists(f))
    return


@app.cell
def _(mo):
    mo.md(r"""We can open one of the BOSS files up to see what it has in it. We'll first just look at what the HDUs are called.""")
    return


@app.cell
def _(astropy, spectrum_files):
    spec_hdulist = astropy.io.fits.open(spectrum_files[5])
    print("Opened FITS spectrum file:", spectrum_files[5])
    print("Total HDU count:", len(spec_hdulist))
    return (spec_hdulist,)


@app.cell
def _(spec_hdulist):
    for ihdu, spec_hdu in enumerate(spec_hdulist):
        if('extname' in spec_hdu.header):
            print(spec_hdu.header['extname'])
        else:
            print("HDU{i}".format(i=ihdu))
    return


@app.cell
def _(mo):
    mo.md(r"""It looks like "COADD" actuall has the spectrum. This is a table, and the columns have the fluxes, wavelengths, masks, etc. Really you should look at the data model at: https://data.sdss.org/datamodel/files/BOSS_SPECTRO_REDUX/RUN2D/spectra/PLATE4/spec.html""")
    return


@app.cell
def _(np, spec_hdulist):
    coadd = np.array(spec_hdulist['COADD'].data)
    coadd_header = spec_hdulist['COADD'].header
    print("COADD table shape:", coadd.shape)
    return coadd, coadd_header


@app.cell
def _(coadd):
    print("Available column names in COADD:")
    print(coadd.dtype.names)
    return


@app.cell
def _(mo):
    mo.md(r"""But if we want to know the units of FLUX or LOGLAM we can check:""")
    return


@app.cell
def _(coadd_header):
    print("TUNIT1 (FLUX unit):", coadd_header['TUNIT1'])
    print("TUNIT2 (LOGLAM unit):", coadd_header['TUNIT2'])
    return


@app.cell
def _(mo):
    mo.md(r"""Now we can plot and label our plot:""")
    return


@app.cell
def _(coadd, plt):
    fig, ax = plt.subplots(figsize=(10, 5))
    if 'LOGLAM' in coadd.dtype.names and 'FLUX' in coadd.dtype.names:
        ax.plot(10**coadd['LOGLAM'], coadd['FLUX'])
        ax.set_xlabel(r'Wavelength (\AA)')
        ax.set_ylabel(r'$f_\lambda$ \rm ($10^{-17}$ erg cm$^{-2}$ s$^{-1}$ \AA$^{-1}$)')
    fig
    return


if __name__ == "__main__":
    app.run()
