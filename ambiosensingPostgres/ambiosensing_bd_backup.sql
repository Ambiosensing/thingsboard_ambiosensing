PGDMP     )                     x            ambiosensing_BD    12.1    12.1      7           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            8           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            9           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            :           1262    16393    ambiosensing_BD    DATABASE     �   CREATE DATABASE "ambiosensing_BD" WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'Portuguese_Portugal.1252' LC_CTYPE = 'Portuguese_Portugal.1252';
 !   DROP DATABASE "ambiosensing_BD";
                postgres    false            �            1259    16543    activation_strategy    TABLE     �   CREATE TABLE public.activation_strategy (
    id integer NOT NULL,
    name character varying,
    profile_idprofile integer NOT NULL
);
 '   DROP TABLE public.activation_strategy;
       public         heap    postgres    false            �            1259    16411    device    TABLE     �   CREATE TABLE public.device (
    id_device integer NOT NULL,
    name character varying NOT NULL,
    type character varying
);
    DROP TABLE public.device;
       public         heap    postgres    false            �            1259    16403    profile    TABLE     n   CREATE TABLE public.profile (
    id_profile integer NOT NULL,
    profile_name character varying NOT NULL
);
    DROP TABLE public.profile;
       public         heap    postgres    false            �            1259    16434    schedule    TABLE     �   CREATE TABLE public.schedule (
    start date NOT NULL,
    "end" date NOT NULL,
    profile_idprofile integer NOT NULL,
    device_iddevice integer NOT NULL
);
    DROP TABLE public.schedule;
       public         heap    postgres    false            �            1259    16582    strategy_alarm    TABLE     �   CREATE TABLE public.strategy_alarm (
    name character varying,
    state character varying,
    act_strgy_id_activation_strategy integer NOT NULL
);
 "   DROP TABLE public.strategy_alarm;
       public         heap    postgres    false            �            1259    16569    strategy_environmental    TABLE     �   CREATE TABLE public.strategy_environmental (
    min numeric,
    max numeric,
    act_strgy_id_activation_strategy integer NOT NULL
);
 *   DROP TABLE public.strategy_environmental;
       public         heap    postgres    false            �            1259    16558    strategy_temporal    TABLE     E  CREATE TABLE public.strategy_temporal (
    monday boolean,
    tuesday boolean,
    wednesday boolean,
    thursday boolean,
    friday boolean,
    saturday boolean,
    sunday boolean,
    spring boolean,
    summer boolean,
    autumn boolean,
    winter boolean,
    act_strgy_id_activation_strategy integer NOT NULL
);
 %   DROP TABLE public.strategy_temporal;
       public         heap    postgres    false            1          0    16543    activation_strategy 
   TABLE DATA           J   COPY public.activation_strategy (id, name, profile_idprofile) FROM stdin;
    public          postgres    false    205   �)       /          0    16411    device 
   TABLE DATA           7   COPY public.device (id_device, name, type) FROM stdin;
    public          postgres    false    203   *       .          0    16403    profile 
   TABLE DATA           ;   COPY public.profile (id_profile, profile_name) FROM stdin;
    public          postgres    false    202   J*       0          0    16434    schedule 
   TABLE DATA           T   COPY public.schedule (start, "end", profile_idprofile, device_iddevice) FROM stdin;
    public          postgres    false    204   y*       4          0    16582    strategy_alarm 
   TABLE DATA           W   COPY public.strategy_alarm (name, state, act_strgy_id_activation_strategy) FROM stdin;
    public          postgres    false    208   �*       3          0    16569    strategy_environmental 
   TABLE DATA           \   COPY public.strategy_environmental (min, max, act_strgy_id_activation_strategy) FROM stdin;
    public          postgres    false    207   �*       2          0    16558    strategy_temporal 
   TABLE DATA           �   COPY public.strategy_temporal (monday, tuesday, wednesday, thursday, friday, saturday, sunday, spring, summer, autumn, winter, act_strgy_id_activation_strategy) FROM stdin;
    public          postgres    false    206   �*       �
           2606    16552 .   activation_strategy activation_strategy_id_key 
   CONSTRAINT     g   ALTER TABLE ONLY public.activation_strategy
    ADD CONSTRAINT activation_strategy_id_key UNIQUE (id);
 X   ALTER TABLE ONLY public.activation_strategy DROP CONSTRAINT activation_strategy_id_key;
       public            postgres    false    205            �
           2606    16550 ,   activation_strategy activation_strategy_pkey 
   CONSTRAINT     }   ALTER TABLE ONLY public.activation_strategy
    ADD CONSTRAINT activation_strategy_pkey PRIMARY KEY (id, profile_idprofile);
 V   ALTER TABLE ONLY public.activation_strategy DROP CONSTRAINT activation_strategy_pkey;
       public            postgres    false    205    205            �
           2606    16418    device device_pkey 
   CONSTRAINT     W   ALTER TABLE ONLY public.device
    ADD CONSTRAINT device_pkey PRIMARY KEY (id_device);
 <   ALTER TABLE ONLY public.device DROP CONSTRAINT device_pkey;
       public            postgres    false    203            �
           2606    16410    profile profile_pkey 
   CONSTRAINT     Z   ALTER TABLE ONLY public.profile
    ADD CONSTRAINT profile_pkey PRIMARY KEY (id_profile);
 >   ALTER TABLE ONLY public.profile DROP CONSTRAINT profile_pkey;
       public            postgres    false    202            �
           2606    16438    schedule schedule_pkey 
   CONSTRAINT     t   ALTER TABLE ONLY public.schedule
    ADD CONSTRAINT schedule_pkey PRIMARY KEY (profile_idprofile, device_iddevice);
 @   ALTER TABLE ONLY public.schedule DROP CONSTRAINT schedule_pkey;
       public            postgres    false    204    204            �
           2606    16589 "   strategy_alarm strategy_alarm_pkey 
   CONSTRAINT     ~   ALTER TABLE ONLY public.strategy_alarm
    ADD CONSTRAINT strategy_alarm_pkey PRIMARY KEY (act_strgy_id_activation_strategy);
 L   ALTER TABLE ONLY public.strategy_alarm DROP CONSTRAINT strategy_alarm_pkey;
       public            postgres    false    208            �
           2606    16576 2   strategy_environmental strategy_environmental_pkey 
   CONSTRAINT     �   ALTER TABLE ONLY public.strategy_environmental
    ADD CONSTRAINT strategy_environmental_pkey PRIMARY KEY (act_strgy_id_activation_strategy);
 \   ALTER TABLE ONLY public.strategy_environmental DROP CONSTRAINT strategy_environmental_pkey;
       public            postgres    false    207            �
           2606    16562 (   strategy_temporal strategy_temporal_pkey 
   CONSTRAINT     �   ALTER TABLE ONLY public.strategy_temporal
    ADD CONSTRAINT strategy_temporal_pkey PRIMARY KEY (act_strgy_id_activation_strategy);
 R   ALTER TABLE ONLY public.strategy_temporal DROP CONSTRAINT strategy_temporal_pkey;
       public            postgres    false    206            �
           2606    16553 6   activation_strategy fk_activation_strategy_profile_idx    FK CONSTRAINT     �   ALTER TABLE ONLY public.activation_strategy
    ADD CONSTRAINT fk_activation_strategy_profile_idx FOREIGN KEY (profile_idprofile) REFERENCES public.profile(id_profile);
 `   ALTER TABLE ONLY public.activation_strategy DROP CONSTRAINT fk_activation_strategy_profile_idx;
       public          postgres    false    2715    202    205            �
           2606    16444     schedule fk_schedule_device1_idx    FK CONSTRAINT     �   ALTER TABLE ONLY public.schedule
    ADD CONSTRAINT fk_schedule_device1_idx FOREIGN KEY (device_iddevice) REFERENCES public.device(id_device);
 J   ALTER TABLE ONLY public.schedule DROP CONSTRAINT fk_schedule_device1_idx;
       public          postgres    false    204    2717    203            �
           2606    16439 !   schedule fk_schedule_profile1_idx    FK CONSTRAINT     �   ALTER TABLE ONLY public.schedule
    ADD CONSTRAINT fk_schedule_profile1_idx FOREIGN KEY (profile_idprofile) REFERENCES public.profile(id_profile);
 K   ALTER TABLE ONLY public.schedule DROP CONSTRAINT fk_schedule_profile1_idx;
       public          postgres    false    204    2715    202            �
           2606    16590 C   strategy_alarm strategy_alarm_act_strgy_id_activation_strategy_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.strategy_alarm
    ADD CONSTRAINT strategy_alarm_act_strgy_id_activation_strategy_fkey FOREIGN KEY (act_strgy_id_activation_strategy) REFERENCES public.activation_strategy(id);
 m   ALTER TABLE ONLY public.strategy_alarm DROP CONSTRAINT strategy_alarm_act_strgy_id_activation_strategy_fkey;
       public          postgres    false    205    2721    208            �
           2606    16577 S   strategy_environmental strategy_environmental_act_strgy_id_activation_strategy_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.strategy_environmental
    ADD CONSTRAINT strategy_environmental_act_strgy_id_activation_strategy_fkey FOREIGN KEY (act_strgy_id_activation_strategy) REFERENCES public.activation_strategy(id);
 }   ALTER TABLE ONLY public.strategy_environmental DROP CONSTRAINT strategy_environmental_act_strgy_id_activation_strategy_fkey;
       public          postgres    false    205    207    2721            �
           2606    16563 I   strategy_temporal strategy_temporal_act_strgy_id_activation_strategy_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.strategy_temporal
    ADD CONSTRAINT strategy_temporal_act_strgy_id_activation_strategy_fkey FOREIGN KEY (act_strgy_id_activation_strategy) REFERENCES public.activation_strategy(id);
 s   ALTER TABLE ONLY public.strategy_temporal DROP CONSTRAINT strategy_temporal_act_strgy_id_activation_strategy_fkey;
       public          postgres    false    2721    206    205            1      x������ � �      /   ,   x�3��IM���)���K<����|.#NGgN�0G�<�=... �h
�      .      x�3�K-J��2���+K-������� NA      0   ,   x�3202�50�52�4�1M99�`\S���Pƈ+F��� v	L      4      x������ � �      3      x������ � �      2      x������ � �     