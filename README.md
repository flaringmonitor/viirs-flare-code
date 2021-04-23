# viirs-flare-code
**Using VIIRS observations and public oil & gas data to model natural gas flaring volumes in near real-time.**
Visit [Flaring Monitor](https://www.flaringmonitor.org/) for more information on this project.

**What is Flaring Monitor?**  
Flaring Monitor is an open-source project that processes and relates NASA satellite sensor readings of heat signatures from natural gas flares to publicly disclosed ownership and reported flaring volumes to estimate the equivalent tons of CO2 emitted by companies in real-time.  

**What is Flaring?**  
Natural gas flaring (&quot;Flaring&quot;) is the controlled disposal of excess natural gas from oil and gas wells, gathering facilities, and refineries into the atmosphere. An attractive option for monitoring natural gas flares is by estimating the quantity of flared natural gas at individual flare stacks and pipes of producing oil and gas wells (&quot;Estimated Flare Volumes&quot;) using infrared signals captured by the National Oceanic and Atmospheric Administration's (&quot;NOAA&quot;) Visible Infrared Imaging Radiometer Suite (&quot;VIIRS&quot;) <sup>[1], [2], [3]</sup>.

By synthesizing satellite-sensor data with oil and gas production and well-meta datasets and Reported Flare Volumes, quantifying site-specific estimations of natural gas flare volumes is achievable in a near-real time and systematic fashion.

**Philosophy**  
The methodologies outlined offer a systematic and objective means of monitoring flaring activity and have the potential to be transferred in other hydrocarbon-producing regions across the world. 

By analyzing both Reported & Estimated Flare Volume and tons of equivalent CO<sub>2</sub> datasets, corporations, governments, and communities can better understand emission levels on a holistic, near real-time basis and more quickly identify where new infrastructure is required. 

**Quick Start**
* Clone this repository to your local computer
* [Visit the website](https://www.flaringmonitor.org/)
* [Read our April 2020 White Paper (see Detailed Methodology section)](https://www.flaringmonitor.org/)
* [Download and process the raw data using Detailed Methodology](https://github.com/flaringmonitor/viirs-flare-data) 

**Development** 

* Clone this repository using git (command-line) or GitKraken (GUI).
* Install Python 3.6+ and run the processing code.

**Contributing** 

* Write your code
* Add tests for new functionality
* Submit a pull request to us with comments indicating what you changed and why
* Reach out to one of the developers on our team if you have any questions

**Need Help?**  
If you run into any issues or facing challenges in recreating the methodology or results, please feel free to reach out to us at contact@flaringmonitor.org.

**References**  

[1]. Elvidge, C.D.; Zhizhin, M.; Hsu, F.-C.; Baugh, K.E. VIIRS Nightfire: Satellite Pyrometry at Night. _Remote Sens._  **2013** , _5_, 4423-4449. [https://doi.org/10.3390/rs5094423](https://doi.org/10.3390/rs5094423)

[2]. Elvidge, C.D.; Zhizhin, M.; Baugh, K.; Hsu, F.-C.; Ghosh, T. Methods for Global Survey of Natural Gas Flaring from Visible Infrared Imaging Radiometer Suite Data. _Energies_  **2016** , _9_, 14. [https://doi.org/10.3390/en9010014](https://doi.org/10.3390/en9010014)

[3]. Colorado School of Mines (n.d.). VIIRS Nightfire (VNF), from https://payneinstitute.mines.edu/eog/viirs-nightfire-vnf/
