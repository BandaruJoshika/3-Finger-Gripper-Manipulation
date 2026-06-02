from setuptools import find_packages, setup

package_name = 'gripper'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='bajajauto',
    maintainer_email='bajajauto@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        'gripper_action_server = gripper.gripper_action_server:main',
        'gripper_action_client = gripper.gripper_action_client:main',
        'gripper_position_publisher = gripper.gripper_position_publisher:main',
        'tcp_rec_publisher = gripper.tcp_rec_publisher:main',
    ],
    },
)
