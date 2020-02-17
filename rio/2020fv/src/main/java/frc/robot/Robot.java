/*----------------------------------------------------------------------------*/
/* Copyright (c) 2017-2018 FIRST. All Rights Reserved.                        */
/* Open Source Software - may be modified and shared by FRC teams. The code   */
/* must be accompanied by the FIRST BSD license file in the root directory of */
/* the project.                                                               */
/*----------------------------------------------------------------------------*/

package frc.robot;

import edu.wpi.first.wpilibj.Compressor;
import edu.wpi.first.wpilibj.TimedRobot;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;

import disc.data.Scenario;
import disc.data.WaypointMap;

import edu.wpi.first.wpilibj.smartdashboard.SmartDashboard;

/**
 * The VM is configured to automatically run this class, and to call the
 * functions corresponding to each mode, as described in the IterativeRobot
 * documentation. If you change the name of this class or the package after
 * creating this project, you must also update the build.properties file in the
 * project.
 */
public class Robot extends TimedRobot {
    /* Here are the instantiations of everything used in the class */
    Climber climb;
    DriveTrain drive;
    Indexing index;
    Intake intake;
    Navigation nav;
    OI oi;
    Shooter shooter;
    Turret turret;
    ExecutorService receiveRunner = Executors.newSingleThreadExecutor();

    DeadReckoning location;

    IMU imu;
    WaypointTravel guidence;
    UDPSender send;
    UDPReceiver receive;
    WaypointMap waypoints;

    Scenario autoScenario;
    Commander auto;

    // Pneumatics
    Compressor compressor;

    @Override
    public void robotInit() {

        oi = new OI();
        drive = new DriveTrain();
        intake = new Intake(oi);
        index = new Indexing(oi, intake);
        climb = new Climber(oi);
        turret = new Turret(oi);
      
        imu = new IMU();
        location = new DeadReckoning(drive, imu);
        guidence = new WaypointTravel(drive, location);
        send = new UDPSender();
        receive = new UDPReceiver();
        nav = new Navigation(oi, drive, guidence);

        shooter = new  Shooter(oi, index, receive);

        compressor = new Compressor(RobotMap.PCM);

        try {
            waypoints = new WaypointMap(new File("/home/lvuser/Waypoints2020.txt"));
            autoScenario = new Scenario(new File("/home/lvuser/TestAuto.txt"));
            SmartDashboard.putBoolean("Suicide", false);
        } 
        catch (FileNotFoundException e) {
            e.printStackTrace();
            SmartDashboard.putBoolean("Suicide", true);
        }

        auto = new Commander(autoScenario, waypoints, location, guidence, intake, index, shooter);
    }

    @Override
    public void autonomousInit() {
        location.reset();
    }

    @Override
    public void autonomousPeriodic() {
        location.updateTracker();
        location.updateDashboard();
        auto.periodic();
    }

    @Override
    public void teleopInit() {
        compressor.setClosedLoopControl(true);
        location.reset();
        //send.sendMessage();
    }

    @Override
    public void teleopPeriodic() {
        location.updateTracker();
        location.updateDashboard();
        nav.navTeleopPeriodic();
        climb.climberTeleopPeriodic();
        intake.intakeTeleopPeriodic();
        index.indexPeriodic();
        shooter.shooterTeleopPeriodic();
        //receiveRunner.submit(receive);
        turret.turretTeleopPeriodic();
    }

    @Override
    public void testPeriodic() {

    }

}