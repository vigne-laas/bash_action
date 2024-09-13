#! /usr/bin/env python
import argparse
import rospy
import actionlib
import yaml
import os
import subprocess
from bash_action.msg import BashAction, BashFeedback, BashResult

class BashActionServer:

    def __init__(self, action_name, config_file):
        self._action_name = action_name
        self._config_file = config_file
        self._action_server = actionlib.SimpleActionServer(self._action_name, BashAction, self.execute_action, True)
        self._action_server.start()

        # Charger le fichier YAML
        try:
            with open(self._config_file, 'r') as file:
                self.actions = yaml.safe_load(file)['actions']
                rospy.loginfo(f"Fichier YAML chargé avec succès : {self._config_file}")
                rospy.loginfo("Actions chargées :")
                for action_name, action_details in self.actions.items():
                    rospy.loginfo(f"Action: {action_name}, Détails: {action_details}")
        except Exception as e:
            rospy.logerr(f"Erreur lors du chargement du fichier YAML : {e}")
            raise e
    def execute_action(self, goal):
        print("Executing action")
        print(goal)
        action_name = goal.action_name
        if action_name in self.actions:
            action_data = self.actions[action_name]
            ros_source_file = action_data.get('ros_source_file', None)
            pre_command = action_data.get('pre_command', '')
            command = action_data.get('command', '')

            success = self.execute_bash_command(ros_source_file, pre_command, command)
            
            # Préparer la réponse finale
            result = BashResult()
            result.success = success
            result.result_message = "Commande exécutée avec succès." if success else "Échec de l'exécution de la commande."
            if success:
                self._action_server.set_succeeded(result)
            else:
                self._action_server.set_aborted(result)
        else:
            rospy.logerr(f"Action {action_name} non trouvée.")
            self._action_server.set_aborted()

    def execute_bash_command(self, ros_source_file, pre_command, main_command):
        # Créer une liste pour la commande complète
        bash_command_parts = []

        # Si un fichier ROS source est fourni, ajoutez la commande source
        if ros_source_file and ros_source_file.strip():
            bash_command_parts.append(f"source {ros_source_file}")

        # Si une commande préalable est fournie, ajoutez-la
        if pre_command and pre_command.strip():
            bash_command_parts.append(pre_command)

        # Ajouter la commande principale si elle est fournie
        if main_command and main_command.strip():
            bash_command_parts.append(main_command)

        # Joindre les parties non vides avec " && " pour exécuter les commandes de manière séquentielle
        bash_command = " && ".join(bash_command_parts)
        rospy.loginfo(f"Commande à exécuter : {bash_command}")
        # S'assurer qu'il y a quelque chose à exécuter
        if bash_command:
            try:
                # Démarrer le processus bash
                process = subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash', text=True)

                # Lire et publier la sortie du processus ligne par ligne
                for stdout_line in iter(process.stdout.readline, ""):
                    rospy.loginfo(stdout_line.strip())  # Log des sorties en temps réel

                    # Envoyer le feedback en temps réel
                    feedback = BashFeedback()
                    feedback.output = stdout_line.strip()
                    self._action_server.publish_feedback(feedback)

                process.stdout.close()
                return_code = process.wait()

                # Vérifier si la commande a réussi
                if return_code == 0:
                    rospy.loginfo("Commande exécutée avec succès.")
                    return True
                else:
                    rospy.logerr("Échec de l'exécution de la commande.")
                    return False
            except Exception as e:
                rospy.logerr(f"Erreur lors de l'exécution de la commande: {str(e)}")
                return False
        else:
            rospy.logwarn("Aucune commande valide à exécuter.")
            return False



if __name__ == '__main__':
    # Initialiser le parser d'arguments
    parser = argparse.ArgumentParser(description="Bash Action Server")
    parser.add_argument('--yaml_path', type=str, required=True, help='Chemin vers le fichier YAML contenant les actions')

    # Récupérer les arguments
    args = parser.parse_args()

    # Initialiser le nœud ROS
    rospy.init_node('bash_action_server')

    rospy.loginfo(f"Utilisation du fichier YAML : {args.yaml_path}")

    # Démarrer le serveur d'actions avec le chemin spécifié
    action_server = BashActionServer('bash_action_server', args.yaml_path)
    rospy.spin()
