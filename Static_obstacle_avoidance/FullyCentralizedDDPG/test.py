
import torch
import numpy as np
import matplotlib.pyplot as plt
from Static_obstacle_avoidance.ApfAlgorithm import APF
from Static_obstacle_avoidance.Method import choose_action, checkPath, drawActionCurve, getReward
device=torch.device("cuda" if torch.cuda.is_available() else "cpu")

if __name__ == "__main__":
    apf = APF()  
    centralizedActor = torch.load('TrainedModel/centralizedActor.pkl',map_location=device) 
    actionCurveDic = {'sphere':np.array([]), 'cylinder':np.array([]), 'cone':np.array([])}

    # apf.drawEnv()       
    q = apf.x0          
    qBefore = [None, None, None]
    rewardSum = 0
    for i in range(500):
        obsDicq = apf.calculateDynamicState(q)
        obs_sphere, obs_cylinder, obs_cone = obsDicq['sphere'], obsDicq['cylinder'], obsDicq['cone']
        obs_mix = obs_sphere + obs_cylinder + obs_cone
        obs = np.array([])  
        for k in range(len(obs_mix)):
            obs = np.hstack((obs, obs_mix[k]))  
        obs = torch.as_tensor(obs, dtype=torch.float, device=device)
        action = centralizedActor(obs).cpu().detach().numpy()
        action_sphere = action[0:apf.numberOfSphere]
        action_cylinder = action[apf.numberOfSphere:apf.numberOfSphere + apf.numberOfCylinder]
        action_cone = action[apf.numberOfSphere + apf.numberOfCylinder:apf.numberOfSphere + \
                             apf.numberOfCylinder + apf.numberOfCone]

        actionCurveDic['sphere'] = np.append(actionCurveDic['sphere'], action_sphere)
        actionCurveDic['cylinder'] = np.append(actionCurveDic['cylinder'], action_cylinder)
        actionCurveDic['cone'] = np.append(actionCurveDic['cone'], action_cone)

        qNext = apf.getqNext(apf.epsilon0, action_sphere, action_cylinder, action_cone, q, qBefore)
        qBefore = q

        flag = apf.checkCollision(qNext)
        rewardSum += getReward(flag, apf, qBefore, q, qNext)

        q = qNext
        if apf.distanceCost(q,apf.qgoal) < apf.threshold:      
            apf.path = np.vstack((apf.path,apf.qgoal))
            
            break

    checkPath(apf,apf.path)
    apf.saveCSV()



    print(rewardSum)

    plt.show()






